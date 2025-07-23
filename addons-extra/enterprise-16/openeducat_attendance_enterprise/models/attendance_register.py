# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import api, fields, models


class OpAttendanceRegister(models.Model):
    _inherit = "op.attendance.register"

    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)
    auto_create = fields.Boolean('Auto Create')
    auto_create_type = fields.Selection([
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly')], 'Auto create sheet duration')
    auto_create_if_session = fields.Boolean('Auto Create If Session')
    subject_id = fields.Many2one('op.subject', string='Subject')
    section_id = fields.Many2one('op.section', string='Section')
    course_id = fields.Many2one('op.course', 'Course', required=False)
    batch_id = fields.Many2one('op.batch', 'Batch', required=False)

    @api.onchange('section_id')
    def onchange_section(self):
        if self.section_id:
            self.batch_id = False
            self.course_id = False

    @api.onchange('subject_id')
    def onchange_subject_id(self):
        self.section_id = False
        if self.subject_id:
            section_ids = self.env['op.section']. \
                search([('subject_id', '=', self.subject_id.id)])
            return {'domain': {'section_id': [('id', 'in', section_ids.ids)]}}

    def action_onboarding_attendance_register_layout(self):
        self.env.user.company_id.\
            onboarding_attendance_register_layout_state = \
            'done'
