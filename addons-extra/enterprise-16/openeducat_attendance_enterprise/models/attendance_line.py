# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import api, fields, models


class OpAttendanceLine(models.Model):
    _inherit = "op.attendance.line"

    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)

    def action_onboarding_attendance_lines_layout(self):
        self.env.user.company_id.onboarding_attendance_lines_layout_state =\
            'done'

    session_id = fields.Many2one(
        related='attendance_id.session_id')
    progression_id = fields.Many2one('op.student.progression',
                                     string="Progression No")

    @api.onchange('student_id')
    def onchange_student_attendance_progrssion(self):
        if self.student_id:
            student = self.env['op.student.progression'].search(
                [('student_id', '=', self.student_id.id)])
            self.progression_id = student.id
            sequence = student.name
            student.write({'name': sequence})
