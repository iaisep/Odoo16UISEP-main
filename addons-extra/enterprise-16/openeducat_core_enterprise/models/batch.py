# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import fields, models


class OpBatch(models.Model):
    _inherit = "op.batch"

    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)
    color = fields.Integer(string='Color Index', default=0)

    student_count = fields.Integer(
        compute="_compute_batch_dashboard_data", string='Student Count')

    def _compute_batch_dashboard_data(self):
        for batch in self:
            student_list = self.env['op.student'].search_count(
                [('course_detail_ids.batch_id', 'in', [batch.id])])
            batch.student_count = student_list

    def action_onboarding_batch_layout(self):
        self.env.user.company_id.onboarding_batch_layout_state = 'done'
