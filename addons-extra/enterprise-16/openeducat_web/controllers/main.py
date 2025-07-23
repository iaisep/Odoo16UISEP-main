# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import http
from odoo.http import request

from odoo.addons.portal.controllers.portal import CustomerPortal


class OpenEduCatWebController(http.Controller):

    """@http.route('/db_register', type='http', auth='user', website=True,
                csrf=False)
    def db_register(self, **post):
        val = {}
        if post and post.get('instance_key'):
            request.env['res.company'].sudo().search([]).write({
                'openeducat_instance_key': post.get('instance_key')
            })
            if not request.env['res.config.settings']. \
                    request_verify_instance_controller(
                        post.get('instance_key')):
                val.update({'invalid_instance': True})
            else:
                val.update({'hash_allow': True})
        if post and post.get('instance_hash_key'):
            request.env['res.company'].sudo().search([]).write({
                'openeducat_instance_hash_key': post.get('instance_hash_key')
            })
            if request.env['res.config.settings'].request_verify_hash(
                    post.get('instance_hash_key')):
                return request.redirect('/web')
            else:
                val.update({'invalid_hash': True, 'hash_allow': True})
        return request.render("openeducat_web.db_registration", val)
        return True

    @http.route('/onesignal/fetch', type='json', auth='none', csrf=False,
                methods=['GET', 'POST'])
    def fetch_onesignal_app_id(self, **kwargs):
        val = {
            'ONESIGNAL_APP_ID': request.env['ir.config_parameter'].
            sudo().get_param('onesignal_app_id'),
        }

        return val
    

    @http.route('/onesignal/register', type='json', auth='none', csrf=False,
                methods=['GET', 'POST'])
    def register_onesignal_device(self, **kwargs):
        if kwargs.get('user_id'):
            user = request.env['res.users'].sudo().search([
                ('id', '=', int(kwargs.get('user_id')))])
            if kwargs.get('userdevice_id'):
                user.update({
                    'onesignal_device_id': kwargs.get('userdevice_id')
                })
                return True
        return False
    """

class OpeneducatPortalMenus(CustomerPortal):

    @http.route(['/my', '/my/home'], type='http', auth="user", website=True)
    def home(self, **kw):
        values = self._prepare_portal_layout_values()

        menu_list = request.env['openeducat.portal.menu'].sudo().search(
            [('is_visible_to_student', '=', True)])
        values.update({'menu_list': menu_list})

        return request.render("portal.portal_my_home", values)
