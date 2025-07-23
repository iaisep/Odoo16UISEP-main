# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import api, fields, models


class OpCourse(models.Model):
    _inherit = 'op.course'

    blog_id = fields.Many2one('blog.blog', 'Blog')
    blog_post_ids = fields.One2many('blog.post', 'course_id',
                                    string='Blog Post')
    blogs_count = fields.Integer(compute='_compute_blog_count')

    @api.depends("blog_post_ids")
    def _compute_blog_count(self):
        for record in self:
            record.blogs_count = len(record.blog_post_ids)

    def action_create_blog(self):
        for record in self:
            if not record.blog_id:
                record.blog_id = self.env['blog.blog'].sudo().create(
                    {'name': record.name})
        return True

    def get_blog(self):
        action = self.env.ref('website_blog.'
                              'action_blog_post').read()[0]
        action['domain'] = [('blog_id', 'in', self.blog_id.ids)]
        return action
