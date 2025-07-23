# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import fields, models


class AttendanceWeightLine(models.Model):

    _name = 'attendance.weight.line'
    _description = "Attendance Weight Line"
    _rec_name = "attendance_type"

    attendance_type = fields.Selection([('present',  'Present'), ('late', 'Late'),
                                        ('excuse', 'Absent Excused'),
                                        ('absent', 'Absent')],
                                       default='present', required=True)
    weightage = fields.Float('Weightage', required=True)
    grade_templates_id = fields.Many2one('op.grade.template.line', 'Grade Template')
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)
