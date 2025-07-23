# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import api, fields, models


class OpSubject(models.Model):
    _inherit = "op.subject"

    course_id = fields.Many2one('op.course', 'Course')
    credit_point = fields.Float('Credit')
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)

    @api.model_create_multi
    def create(self, vals):
        res = super(OpSubject, self).create(vals)
        res.course_id.write({'subject_ids': [(4, res.id)]})
        return res

    def write(self, vals):
        self.course_id.write({'subject_ids': [(3, self.id)]})
        super(OpSubject, self).write(vals)
        self.course_id.write({'subject_ids': [(4, self.id)]})
        return self

    def action_onboarding_subject_layout(self):
        self.env.user.company_id.onboarding_subject_layout_state = 'done'
