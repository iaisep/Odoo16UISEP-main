import json
import os
import subprocess

import werkzeug
from O365 import Account, FileSystemTokenBackend

from odoo import http
from odoo.http import request

dir_path = os.path.dirname(os.path.realpath(__file__))


class AuthController(http.Controller):
    @http.route('/get_auth_url/<int:current_id>',
                type='http', methods=['GET', 'POST'], auth='public')
    def get_auth_url(self, current_id=None, **post):
        global dir_path

        self.res_config = request.env['res.config.settings'].sudo().search(
            [('id', '=', int(current_id))])

        self.credentials = (self.res_config.application_id,
                            self.res_config.client_secret)

        self.scopes = ['offline_access', 'https://graph.microsoft.com/User.Read',
                       'https://graph.microsoft.com/OnlineMeetings.Read',
                       'https://graph.microsoft.com/OnlineMeetings.ReadWrite']

        self.token_backend = FileSystemTokenBackend(
            token_path=dir_path, token_filename='ms_token.txt')

        account = Account(credentials=self.credentials,
                          scopes=self.scopes, token_backend=self.token_backend)

        if account.is_authenticated:
            pass
        else:
            self.callback = self.res_config.redirect_url

            self.url, self.state = account.con.get_authorization_url(
                requested_scopes=self.scopes, redirect_uri=self.callback)

            return werkzeug.utils.redirect(self.url)

    @http.route('/get_auth_token', type='http',
                methods=['GET'], auth='public', website=True)
    def get_auth_token(self):
        global dir_path
        account = Account(credentials=self.credentials,
                          scopes=self.scopes, token_backend=self.token_backend)
        token_url = request.httprequest.url.split(":")

        res_config = request.env['res.config.settings'].sudo().search([])

        for n, i in enumerate(token_url):
            if i == 'http':
                token_url[n] = 'https'
                final_token_url = ':'.join(token_url)
            else:
                final_token_url = ':'.join(token_url)

        result = account.con.request_token(
            final_token_url, state=self.state,
            redirect_uri=self.callback, store_token=True)

        if result:
            with open('{}/ms_token.txt'.format(dir_path), 'r') as openfile:
                json_file = json.load(openfile)
            for res in res_config:
                if res.id == self.res_config.id:
                    res.update(
                        {
                            "access_token": json_file['access_token'],
                            "bearer_token": json_file
                        }
                    )
                    res.get_values()
                    res.set_values()
            subprocess.call(['rm', '-rf', '{}/ms_token.txt'.format(dir_path)])
            return request.render('openeducat_teams.token_confirmed')

        else:
            return request.render('openeducat_teams.token_refused')
