# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import fields, models


class OpBlogPost(models.Model):
    _inherit = "blog.post"

    alumni_group_id = fields.Many2one('op.alumni.group', string='Alumni Group')


class Opalumni(models.Model):
    _inherit = "op.alumni.group"

    blog_post_ids = fields.One2many(
        'blog.post', 'alumni_group_id', string='Blog')
