# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import http
from odoo.http import request


class AlumniWeb(http.Controller):

    @http.route('/alumni', type='http', auth='public', website=True)
    def alumni_group(self, **kwargs):
        alumni_id = request.env['op.alumni.group'].sudo().search([])

        return request.render('openeducat_alumni_enterprise.alumni_page', {
            'alumni_id': alumni_id
        })

    @http.route([
        '/alumni/detail/<model("op.alumni.group"):alumni>'],
        type='http', auth='public', website=True)
    def alumni_detail(self, alumni, **kwargs):
        alumni_id = alumni.sudo().alumni_student_line
        return http.request.render('openeducat_alumni_enterprise.alumni_group',
                                   {'alumni': alumni,
                                    'alumni_id': alumni_id})

    # @http.route([
    #     '/alumni/detail/<model("op.alumni.group"):alumni>/<int:student>'],
    #     type='http', auth="public",sitemap=False, website=True)
    # def jobpost_detail(self, student, alumni, **kwargs):
    #     student_obj = request.env['op.student']
    #     student_id = student_obj.sudo().search([('id', '=', student)])
    #     return request.render("openeducat_alumni_enterprise.student_detail", {
    #         'student': student_id,
    #     })

    @http.route(['/alumni/user/<int:user_id>/avatar'],
                type='http', auth="public", website=True, sitemap=False)
    def user_avatar(self, user_id, field='image_1920',
                    width=0, height=0, crop=False, **post):
        return request.env['ir.binary']._get_image_stream_from(
            request.env['op.student'].sudo().browse(int(user_id)),
            field_name=field, width=int(width),
            height=int(height), crop=crop
        ).get_response()
