# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import api, fields, models


class OpGradeTemplateLine(models.Model):
    _name = 'op.grade.template.line'
    _description = "Grade Template Line"
    _rec_name = "academic_years_id"

    academic_years_id = fields.Many2one('op.academic.year', 'Academic Year',
                                        required=True)
    academic_term_id = fields.Many2one('op.academic.term', 'Terms')
    grade_template_id = fields.Many2one('op.grade.template', 'Grade Template')
    assignment_type_id = fields.Many2one('grading.assignment.type', 'Assignment Type',)
    percentage = fields.Float('Percentage')

    weightage = fields.Selection([('sub_term', 'Sub Term weightage'),
                                  ('aasignment_type', 'Assignment Type Weightage'),
                                  ('attendance_type', 'Attendance Weightage')],
                                 'Weightage Type', required=True, default='sub_term')
    subterm_weight_ids = fields.One2many('subterm.weight.line', 'grade_template_id',
                                         string='Subterm Weight')
    assignment_type_weight_ids = fields.One2many('assignment.type.weight.line',
                                                 'grade_templates_id',
                                                 string='Assignment Weight')
    attendance_type_weight_ids = fields.One2many('attendance.weight.line',
                                                 'grade_templates_id',
                                                 string='Attendance Weight')
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)

    @api.onchange('academic_years_id')
    def terms_by_year(self):
        lists = []
        year_id = self.env['op.academic.year'].search([('id', '=',
                                                        self.academic_years_id.id)])
        for i in year_id.academic_term_ids:
            lists.append(i.id)
        domain = {'academic_term_id': [('id', 'in', lists)]}
        result = {'domain': domain}
        return result
