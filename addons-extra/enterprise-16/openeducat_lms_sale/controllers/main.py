# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import http
from odoo.http import request

from odoo.addons.openeducat_lms.controllers.main import OpenEduCatLms


class OpenEduCatLmsSale(OpenEduCatLms):

    @http.route()
    def enroll_course(self, course, **kwargs):
        if course.type == 'free':
            super(OpenEduCatLmsSale, self).enroll_course(course, **kwargs)
            return request.redirect('/my-courses')
        else:
            super(OpenEduCatLmsSale, self).enroll_course(course, **kwargs)
            enrollment = request.env['op.course.enrollment'].sudo().search([
                ('user_id', '=', request.env.user.id),
                ('course_id', '=', course.id)])
            enrollment.sudo().state = 'draft'
            order_sudo = request.website.sale_get_order(force_create=True)
            order_sudo._cart_update(product_id=course.product_id.id, add_qty=1)
            enrollment.sudo().order_id = order_sudo
            return request.redirect('/shop/cart')
