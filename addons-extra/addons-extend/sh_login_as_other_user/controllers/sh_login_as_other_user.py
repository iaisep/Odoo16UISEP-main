# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from uuid import uuid4
from odoo.http import request, route

from odoo.addons.web.controllers.session import Session
from odoo.addons.web.controllers.home import Home

SCOPE = 'sh_login'


def _sh_login(uid):
    request.session.pre_uid = int(uid)
    request.session.pre_login = int(uid)
    request.session.finalize(request.env)
    request.update_context = request.session.context


class LoginAsHome(Home):

    @route('/web/sh_login', type='http', auth='user', sitemap=False)
    def login_as(self, uid=None, **kwargs):
        key = False
        user = request.env.user
        if uid:
            key = user.env['res.users.apikeys']._generate(
                SCOPE, uuid4().hex)
            _sh_login(uid)
        response = request.redirect(
            self._login_redirect(request.session.uid))
        if key:
            response.set_cookie(SCOPE, key)
        return response


class LoginAsSession(Session):

    @route('/web/session/logout', type='http', auth="none")
    def logout(self, redirect='/web'):
        key = request.httprequest.cookies.get(SCOPE)
        if key:
            result = request.env['res.users.apikeys']._check_credentials(
                scope=SCOPE, key=key)
            if result:
                for apikey in request.env['res.users.apikeys'].sudo().search([
                    ('user_id', '=', result),
                    ('scope', '=', SCOPE),
                ]):
                    apikey._remove()
        response = super().logout(redirect)
        if request.httprequest.cookies.get(SCOPE):
            response.delete_cookie(SCOPE)
        return response
