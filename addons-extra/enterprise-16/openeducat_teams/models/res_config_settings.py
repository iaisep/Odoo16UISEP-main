# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

import json
import os
import subprocess

from O365 import Account, FileSystemTokenBackend

from odoo import api, fields, models
from odoo.http import request


class TeamsConfig(models.TransientModel):

    _inherit = 'res.config.settings'

    application_id = fields.Char(string="Application Id", store=True)
    client_secret = fields.Char(string="Client Secret", store=True)
    redirect_url = fields.Char(
        string="Redirect URL", readonly=True)
    access_token = fields.Char(
        string="Access Token", readonly=True)
    bearer_token = fields.Char()
    webhook_url = fields.Char(string="Webhook URL", store=True)
    send_card_globally = fields.Boolean(
        string="Send Card for General", store=True)
    send_card_course = fields.Boolean(
        string="Send Card for Course", store=True)
    res_id = fields.Integer()

    def auth_token(self):
        scopes = ['https://graph.microsoft.com/User.Read',
                  'https://graph.microsoft.com/OnlineMeetings.Read',
                  'https://graph.microsoft.com/OnlineMeetings.ReadWrite']
        account = Account(scopes=scopes, credentials=(
            self.application_id, self.client_secret))
        if account.is_authenticated:
            return True
        else:
            callback = str(request.httprequest.host_url) + \
                'get_auth_url/%s' % self.id
            return {
                'type': 'ir.actions.act_url',
                'url': callback,
                'target': 'new',
                'res_id': self.id,
            }

    @api.model
    def default_get(self, fields):

        res = super(TeamsConfig, self).default_get(fields)

        try:
            token_url = str(
                request.httprequest.environ['HTTP_ORIGIN']) + "/get_auth_token/"

            res.update({
                'redirect_url': token_url,
            })
            return res

        except Exception:
            res.update({
                'redirect_url': 'token_url',
            })
            return res

    @api.model
    def get_values(self):

        res = super(TeamsConfig, self).get_values()
        res.update(
            application_id=self.env['ir.config_parameter'].sudo(
            ).get_param('application.id'),
            client_secret=self.env['ir.config_parameter'].sudo(
            ).get_param('client.secret'),
            webhook_url=self.env['ir.config_parameter'].sudo(
            ).get_param('webhook.url'),
            access_token=self.env['ir.config_parameter'].sudo(
            ).get_param('access.token'),
            send_card_globally=self.env['ir.config_parameter'].sudo(
            ).get_param('ms.send.card'),
            send_card_course=self.env['ir.config_parameter'].sudo(
            ).get_param('course.send.card'),
            bearer_token=self.env['ir.config_parameter'].sudo(
            ).get_param('ms.bearer.token')
        )
        return res

    def set_values(self):

        super(TeamsConfig, self).set_values()

        param = self.env['ir.config_parameter'].sudo()

        param.set_param('application.id',
                        self.application_id)

        param.set_param('client.secret', self.client_secret)

        param.set_param('webhook.url', self.webhook_url)

        param.set_param('access.token', self.access_token)

        param.set_param('ms.send.card', self.send_card_globally)

        param.set_param('course.send.card', self.send_card_course)

        param.set_param('ms.bearer.token', self.bearer_token)

    def do_refresh_token(self):

        res_config = self.env['ir.config_parameter'].sudo()

        access_token_key = res_config.search([('key', '=', 'ms.bearer.token')])
        app_id_key = res_config.search([('key', '=', 'application.id')])
        client_key = res_config.search([('key', '=', 'client.secret')])
        access_token = access_token_key.value
        dir_path = os.path.dirname(os.path.realpath(__file__))
        with open('{}/ms_token.txt'.format(dir_path), 'w') as openfile:
            openfile.write(access_token.replace("'", '"'))

        scopes = ['offline_access', 'https://graph.microsoft.com/User.Read',
                  'https://graph.microsoft.com/OnlineMeetings.Read',
                  'https://graph.microsoft.com/OnlineMeetings.ReadWrite']

        token_backend = FileSystemTokenBackend(
            token_path=dir_path, token_filename='ms_token.txt')

        credentials = (app_id_key.value, client_key.value)

        account = Account(credentials=credentials,
                          scopes=scopes, token_backend=token_backend)

        account.con.refresh_token()
        with open('{}/ms_token.txt'.format(dir_path), 'r') as openfile:
            json_file = json.load(openfile)

        self.env['ir.config_parameter'].sudo().set_param(
            'access.token', json_file['access_token'])
        self.env['ir.config_parameter'].sudo().set_param(
            'ms.bearer.token', json_file)
        subprocess.call(['rm', '-rf', '{}/ms_token.txt'.format(dir_path)])
