# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import api, fields, models


class BlogPost(models.Model):
    _inherit = "blog.post"

    course_id = fields.Many2one('op.course', 'Course')

    @api.onchange('blog_id')
    def _onchange_blog_id(self):
        if self.blog_id:
            course = self.env['op.course'].search([('blog_id', '=', self.blog_id.id)])
            self.course_id = course
