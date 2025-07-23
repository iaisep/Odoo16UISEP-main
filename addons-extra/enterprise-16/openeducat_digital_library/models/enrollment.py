# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################
from odoo import fields, models


class OpDigitalLibraryEnrollment(models.Model):
    _name = "op.digital.library.enrollment"
    _rec_name = "user_id"
    _description = "Digital Library Enrollment"

    category_id = fields.Many2one('op.digital.library.category', string="Category")
    enrollment_date = fields.Datetime('Enrollment Date', required=True,
                                      default=fields.Datetime.now())
    user_id = fields.Many2one(
        'res.users', 'User', required=True, ondelete="cascade")
    material_id = fields.Many2one('op.digital.library.material', string="Material")
    active = fields.Boolean(default=True)
    state = fields.Selection([('draft', 'Draft'),
                              ('in_progress', 'In Progress'),
                              ('reading_list', 'Reading List')],
                             'State', default='draft')
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)
    last_access = fields.Datetime('Last Access', default=False)
