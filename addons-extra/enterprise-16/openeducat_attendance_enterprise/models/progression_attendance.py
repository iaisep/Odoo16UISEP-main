# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import api, fields, models


class StudentProgression(models.Model):
    _inherit = ["op.student.progression"]

    @api.depends("attendance_lines")
    def _compute_total_attendance(self):
        self.total_attendance = len(self.attendance_lines)

    attendance_lines = fields.One2many('op.attendance.line',
                                       'progression_id',
                                       string='Progression Attendance')
    total_attendance = fields.Integer('Total Attendance',
                                      compute="_compute_total_attendance",
                                      store=True)
