# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import fields, models


class OpAlumniGroup(models.Model):
    _name = "op.alumni.group"
    _inherit = ['mail.thread', 'website.seo.metadata',
                'website.published.multi.mixin']
    _description = "Alumni Group"

    name = fields.Char(string="Name", tracking=True)
    description = fields.Html(string="Description")
    image = fields.Image()
    alumni_student_line = fields.One2many('op.student',
                                          'alumni_id', string='Students',
                                          tracking=True)
    forum_id = fields.Many2one('forum.forum', string='Forum', readonly=True)
    fees_id = fields.Many2one('product.product', string='Fees')
    alumni_fees_amount = fields.Float(string="Fees Amount")
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)
    active = fields.Boolean(default=True)

    def createforum(self):
        users_res = self.env['forum.forum']
        for record in self:
            if not record.forum_id:
                forum_id = users_res.create({
                    'name': record.name,
                })
                record.forum_id = forum_id
