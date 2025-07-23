# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
from odoo.http import request
from odoo import api, models

SCOPE = 'sh_login'


def _sh_login(uid):
    request.session.pre_uid = int(uid)
    request.session.finalize()
    request.context = request.session.context


class LoginUser(models.Model):
    _inherit = 'res.users'

    @api.model
    def check_login_enabled(self, kw):
        user = self.env['res.users'].browse(kw)
        if user.user_has_groups('sh_login_as_other_user.sh_allow_login_as_other_user') or user.user_has_groups('sh_login_as_other_user.sh_allow_login_as_other_user_only_portal'):
            return True
        key = request.httprequest.cookies.get(SCOPE)
        if key:
            result = request.env['res.users.apikeys']._check_credentials(
                scope=SCOPE, key=key)
            if result:
                return True
        return False

    @api.model
    def sh_logout(self, kw):
        uid = self._get_origin_user_id()
        if uid:
            _sh_login(uid)
            response = request.redirect('/web/'+str(uid))
            if request.httprequest.cookies.get(SCOPE):
                response.delete_cookie(SCOPE)
            return response

    def _get_origin_user_id(self):
        key = request.httprequest.cookies.get(SCOPE)
        if key and request.env:
            result = request.env['res.users.apikeys']._check_credentials(
                scope=SCOPE, key=key)
            if result:
                for apikey in request.env['res.users.apikeys'].sudo().search([
                    ('user_id', '=', result),
                    ('scope', '=', SCOPE),
                ]):
                    apikey._remove()
            return result
