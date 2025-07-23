# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import api, fields, models


class OpMarksheetLine(models.Model):
    _inherit = "op.marksheet.line"

    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)

    progression_id = fields.Many2one('op.student.progression',
                                     string="Progression No")
    exam_name = fields.Many2one(
        related='result_line.exam_id.session_id')
    exam_type = fields.Many2one(
        related='result_line.exam_id.session_id.exam_type')
    grand_total = fields.Integer("Grand Total",
                                 compute='_compute_grand_total')

    @api.onchange('student_id')
    def onchange_student_marksheet_line_progrssion(self):
        if self.student_id:
            student = self.env['op.student.progression'].search(
                [('student_id', '=', self.student_id.id)])
            self.progression_id = student.id
            sequence = student.name
            student.write({'name': sequence})

    def _compute_grand_total(self):
        for record in self:
            record.grand_total = sum([
                int(record.exam_id.total_marks) for record in record.result_line])

    def search_read_for_result(self):

        if self.env.user.partner_id.is_student:
            user = self.env.user
            student_id = self.env['op.student'].sudo().search(
                [('user_id', '=', user.id)])
            marksheet_id = self.sudo().search(
                [('student_id', '=', student_id.id)])
            res = []
            for marksheet in marksheet_id:
                my_dict = {
                    'percentage': marksheet.percentage,
                    'total_marks': marksheet.total_marks,
                    'status': marksheet.status,
                    'grade': marksheet.grade,
                    'id': marksheet.id,
                    'result_line': [result.id for result in marksheet.result_line],
                    'student_id': marksheet.student_id.name,
                    'exam_name': [(result.exam_id.session_id.name)
                                  for result in marksheet.result_line],
                    'exam_type': [(result.exam_id.session_id.exam_type.name)
                                  for result in marksheet.result_line],
                    'grand_total': sum(int(result.exam_id.total_marks)
                                       for result in marksheet.result_line)
                }
                res.append(my_dict)
            return res
