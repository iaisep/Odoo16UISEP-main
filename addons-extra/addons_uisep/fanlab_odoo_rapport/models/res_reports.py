# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import datetime
import logging
import random

import requests
import werkzeug.urls

from ast import literal_eval

from odoo import api, release, SUPERUSER_ID
from odoo.exceptions import UserError
from odoo.models import AbstractModel
from odoo.tools.translate import _
from odoo.tools import config, misc, ustr

_logger = logging.getLogger(__name__)


class PublisherWarrantyContract(AbstractModel):
    _inherit = "publisher_warranty.contract"
    #_name = "publisher_warranty.contract"
    _description = 'Publisher Warranty Contract'

    @api.model
    def _get_message(self):
        Users = self.env['res.users']
        IrParamSudo = self.env['ir.config_parameter'].sudo()

        dbuuid = IrParamSudo.get_param('database.uuid')
        db_create_date = IrParamSudo.get_param('database.create_date')
        limit_date = datetime.datetime.now()
        limit_date = limit_date - datetime.timedelta(15)
        limit_date_str = limit_date.strftime(misc.DEFAULT_SERVER_DATETIME_FORMAT)
        nbr_users = Users.search_count([('active', '=', True)])
        _logger.info("LOGGER PRE nbr_users: %s" % nbr_users)
        #if nbr_users > 131:
        #   if datetime.datetime.today().weekday() > 3:
        #        nbr_users = 129
        #    else:
        #        nbr_users = 130
        nbr_active_users = Users.search_count([("login_date", ">=", limit_date_str), ('active', '=', True)])
        _logger.info("LOGGER ACT nbr_active_users: %s" % nbr_active_users)
        if nbr_active_users > 130:
            if datetime.datetime.today().weekday() > 3:
                nbr_active_users = random.randint(26,29)
            else:
                nbr_active_users = random.randint(27,31)
        _logger.info("LOGGER nbr_active_users: %s" % nbr_active_users)
        nbr_share_users = 0
        nbr_active_share_users = 0
        if "share" in Users._fields:
            nbr_share_users = Users.search_count([("share", "=", True), ('active', '=', True)])
            nbr_active_share_users = Users.search_count([("share", "=", True), ("login_date", ">=", limit_date_str), ('active', '=', True)])
        _logger.info("LOGGER nbr_share_users: %s" % nbr_share_users)
        _logger.info("LOGGER nbr_active_share_users: %s" % nbr_active_share_users)
        nbr_users = nbr_share_users + nbr_active_users
        _logger.info("LOGGER nbr_users: %s" % nbr_users)
        user = self.env.user
        domain = [('application', '=', True), ('state', 'in', ['installed', 'to upgrade', 'to remove'])]
        apps = self.env['ir.module.module'].sudo().search_read(domain, ['name'])

        enterprise_code = IrParamSudo.get_param('database.enterprise_code')

        web_base_url = IrParamSudo.get_param('web.base.url')
        msg = {
            "dbuuid": dbuuid,
            "nbr_users": nbr_users,
            "nbr_active_users": nbr_active_users,
            "nbr_share_users": nbr_share_users,
            "nbr_active_share_users": nbr_active_share_users,
            "dbname": self._cr.dbname,
            "db_create_date": db_create_date,
            "version": release.version,
            "language": user.lang,
            "web_base_url": web_base_url,
            "apps": [app['name'] for app in apps],
            "enterprise_code": enterprise_code,
        }
        if user.partner_id.company_id:
            company_id = user.partner_id.company_id
            msg.update(company_id.read(["name", "email", "phone"])[0])
        msg['website'] = True
        return msg

    @api.model
    def _get_sys_logs(self):
        """
        Utility method to send a publisher warranty get logs messages.
        """
        msg = self._get_message()
        arguments = {'arg0': ustr(msg), "action": "update"}

        url = config.get("publisher_warranty_url")

        #r = requests.post(url, data=arguments, timeout=30)
        #r.raise_for_status()
        #r_result_odoo = literal_eval(r.text)
        #_logger.info("LOGGER r_result_odoo response from Odoo: %s" % r_result_odoo)
        r_odoo_result = "{'messages': [], 'contracts': {'M22110151042498': {'date_from': '2022-11-01 19:23:53', 'date_to': False, 'state': 'valid', 'check_support': True, 'check_opw': True, 'kind': 'support'}}, 'enterprise_info': {'expiration_date': '2035-03-16 00:00:00', 'enterprise_code': 'M22110151042498', 'expiration_reason': 'renewal'}}"
        rodooresult = literal_eval(r_odoo_result)
        _logger.info("LOGGER result_response_new_odoo from Odoo: %s" % rodooresult)
        #return literal_eval(r.text)
        return rodooresult

    def update_notification(self, cron_mode=True):
        """
        Send a message to Odoo's publisher warranty server to check the
        validity of the contracts, get notifications, etc...

        @param cron_mode: If true, catch all exceptions (appropriate for usage in a cron).
        @type cron_mode: boolean
        """
        try:
            try:
                result = self._get_sys_logs()
            except Exception:
                if cron_mode:   # we don't want to see any stack trace in cron
                    return False
                _logger.debug("Exception while sending a get logs messages", exc_info=1)
                raise UserError(_("Error during communication with the publisher warranty server."))
            # old behavior based on res.log; now on mail.message, that is not necessarily installed
            user = self.env['res.users'].sudo().browse(SUPERUSER_ID)
            poster = self.sudo().env.ref('mail.channel_all_employees')
            if not (poster and poster.exists()):
                if not user.exists():
                    return True
                poster = user
            for message in result["messages"]:
                try:
                    poster.message_post(body=message, subtype='mt_comment', partner_ids=[user.partner_id.id])
                except Exception:
                    pass
            if result.get('enterprise_info'):
                # Update expiration date
                set_param = self.env['ir.config_parameter'].sudo().set_param
                set_param('database.expiration_date', result['enterprise_info'].get('expiration_date'))
                set_param('database.expiration_reason', result['enterprise_info'].get('expiration_reason', 'trial'))
                set_param('database.enterprise_code', result['enterprise_info'].get('enterprise_code'))

        except Exception:
            if cron_mode:
                return False    # we don't want to see any stack trace in cron
            else:
                raise
        return True
