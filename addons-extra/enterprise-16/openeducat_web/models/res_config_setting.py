# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

import datetime

import requests
from dateutil import parser

from odoo import _, api, exceptions, fields, models

API_ENDPOINT = "https://openeducat.org"
REQUEST_REGISTER_CONTRACT = '%s/register/contract' % API_ENDPOINT
REQUEST_REGISTER_HASH_CONTRACT = '%s/register/instance-hash' % API_ENDPOINT
URLOPEN_TIMEOUT = 10


class ResCompany(models.Model):
    _inherit = 'res.company'
    openeducat_instance_key = fields.Char("OpenEducat Instance Key")
    openeducat_instance_hash_key = fields.Char(
        "OpenEducat Instance Hash Key",
        help='Instance Hash key is correspondence to '
             'instance key which you get in mail.')
    is_mail_sent = fields.Boolean('Is Mail Sent')
    verify_date = fields.Char('Verify Date')
    openeducat_instance_hash_msg = fields.Char(
        'Instance Hash Key Message',
        default='Check your mail! OpenEduCat Instance '
                'Hash key has been sent successfully.')
    is_hash_verified = fields.Boolean("Is Hash Verified")


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    openeducat_instance_key = fields.Char(
        string="OpenEducat Instance Key",
        readonly=False,
        related="company_id.openeducat_instance_key")
    openeducat_instance_hash_key = fields.Char(
        "OpenEducat Instance Hash Key", readonly=False,
        related="company_id.openeducat_instance_hash_key",
        help="Instance Hash key is correspondence to "
             "instance key which you get in mail.")
    is_mail_sent = fields.Boolean(related="company_id.is_mail_sent")
    openeducat_instance_hash_msg = fields.Char(
        related="company_id.openeducat_instance_hash_msg")
    verify_date = fields.Char(related="company_id.verify_date")
    is_hash_verified = fields.Boolean(related="company_id.is_hash_verified")

    def verify_instance(self):
        if not self.request_verify_instance(self.openeducat_instance_key):
            raise exceptions.UserError(_('Invalid Instance key.'))

    def verify_hash(self):
        if not self.request_verify_hash(self.openeducat_instance_hash_key):
            raise exceptions.UserError(
                _('Instance key and Hash key mismatch.'))

    def request_verify_instance(self, key):
        r = requests.post(
            REQUEST_REGISTER_CONTRACT,
            data={'key': key},
            timeout=URLOPEN_TIMEOUT,
        )
        if r.status_code == 200:
            company = self.env['res.company'].search([])
            for record in company:
                record.write({
                    "is_mail_sent": True,
                    "openeducat_instance_key": self.openeducat_instance_key})
            return True
        else:
            return False

    def request_verify_instance_controller(self, key):
        r = requests.post(
            REQUEST_REGISTER_CONTRACT,
            data={'key': key},
            timeout=URLOPEN_TIMEOUT,
        )
        if r.status_code == 200:
            company = self.env['res.company'].search([])
            for r in company:
                r.write({
                    "is_mail_sent": True})
            return True
        else:
            return False

    def request_verify_hash(self, key):
        r = requests.post(
            REQUEST_REGISTER_HASH_CONTRACT,
            data={'key': key},
            timeout=URLOPEN_TIMEOUT,
        )
        if r.status_code == 200:
            data = r.json()
            company = self.env['res.company'].search([])
            for record in company:
                if data['contract_instance_key'] == \
                        record.openeducat_instance_key:
                    conf_param = self.env['ir.config_parameter']
                    conf_param.set_param('database.openeducat_expire_date',
                                         data['contract_expires'])
                    conf_param.set_param('database.hash_validated_date',
                                         data['hash_validated_date'])
                    conf_param.set_param('database.openeducat_instance_key',
                                         data['contract_instance_key'])
                    conf_param. \
                        set_param('database.openeducat_instance_hash_key',
                                  self.openeducat_instance_hash_key)

                    self.write({
                        "verify_date": data['contract_expires'],
                        "openeducat_instance_hash_msg": 'Hash Key Verified!',
                    })
                    record.write({
                        "openeducat_instance_hash_key": key,
                        "verify_date": data['contract_expires'],
                        "openeducat_instance_hash_msg": 'Hash Key Verified!',
                        "is_hash_verified": True})
                else:
                    record.write({"is_hash_verified": False})
            return True
        else:
            return False

    def verify_database(self):
        now = datetime.datetime.now()
        config = self.env['ir.config_parameter'].sudo()
        db_expire_date = config.get_param('database.openeducat_expire_date')
        if not db_expire_date:
            db_create_date = config.get_param('database.create_date')
        if db_expire_date:
            db_expire_date = parser.parse(db_expire_date)
            diffDate = db_expire_date.date() - now.date()
            diffDate = diffDate.days
        else:
            db_create_date = parser.parse(db_create_date)
            diffDate = now.date() - db_create_date.date()
            diffDate = 15 - diffDate.days
        return diffDate


class IrConfigParameter(models.Model):
    _inherit = "ir.config_parameter"

    def write(self, val):
        if self.key == 'database.openeducat_expire_date' and not val.get(
                'is_renew'):
            val['value'] = self.value
        if val.get('is_renew'):
            del val['is_renew']
        return super(IrConfigParameter, self).write(val)

    @api.model
    def set_param(self, key, value):
        """Sets the value of a parameter.

        :param string key: The key of the parameter value to set.
        :param string value: The value to set.
        :return: the previous value of the parameter or False if it did
                 not exist.
        :rtype: string
        """
        param = self.search([('key', '=', key)])
        if param:
            old = param.value
            if value is not False and value is not None:
                if key == 'database.openeducat_expire_date':
                    param.write({'value': value, 'is_renew': True})
                else:
                    param.write({'value': value})
            else:
                param.unlink()
            return old
        else:
            if value is not False and value is not None:
                self.create({'key': key, 'value': value})
            return False
