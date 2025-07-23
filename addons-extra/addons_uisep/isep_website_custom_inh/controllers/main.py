from odoo import fields, http, modules, tools
from odoo.http import request, route
from odoo.addons.isep_website_custom.controllers.main import DashboardPortal
import logging
import pprint
_logger = logging.getLogger(__name__)




class DashboardPortalInh(DashboardPortal):

    @route(['/campus'], type='http', auth="user", website=True)
    def view_user_profile(self, **post):
        user_id = request.env.user.id
        user = self._check_user_profile_access(user_id)
        if not user:
            return request.render("website_profile.private_profile")
        values = self._prepare_user_values(**post)
        params = self._prepare_user_profile_parameters(**post)
        values.update(self._prepare_user_profile_values(user, **params))

        # values = self._prepare_portal_layout_values()

        menu_list = request.env['openeducat.portal.menu'].sudo().search(
            [('is_visible_to_student', '=', True)])
        values.update({'menu_list': menu_list})
        invoice_ids = request.env['account.move'].search([('partner_id','=',user.partner_id.id),('move_type','=','out_invoice'),('state','=','posted'),('payment_state','=','not_paid'),('invoice_date_due','<',fields.Date.today())])        
        if len(invoice_ids) > 1 : #cambia la cantidad de dias que se consideran vencidos
            values['menu_list'] = request.env['openeducat.portal.menu']
            values['courses_ongoing'] = False
            return request.render("isep_website_custom_inh.campus_pending_payments")
        return request.render("website_profile.user_profile_main", values)

    

    @http.route(['/campus/course/<int:course_id>'], type='http', auth="user", website=True)
    def view_user_profile_course(self, course_id, **post):
        """user = self._check_user_profile_access(course_id)
        if not user:
            return request.render("website_profile.private_profile")
        values = self._prepare_user_values(**post)
        
        params = self._prepare_user_profile_parameters(**post)
        values.update(self._prepare_user_profile_values(user, **params))"""
        user_id = request.env.user.id
        user = self._check_user_profile_access(user_id)
        values = self._prepare_user_values(**post)
        params = self._prepare_user_profile_parameters(**post)
        values.update(self._prepare_user_profile_values(user, **params))

        #subjects = request.env['op.subject'].sudo().search([('course_id','=', int(course_id) )])
        #course = request.env['op.course'].sudo().browse(course_id)
        #subject_ids = []
        #for line in course.sudo().subject_ids:
        #    subject_ids.append(line.id)


        # values['op_subject_ids'] = subject_ids
        values['op_course_id'] = course_id


        _logger.info('********** values: %s' % pprint.pformat(values))

        return request.render("isep_website_custom.user_profile_course", values)

 
    
