# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright(C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class OpAssignmentSubLine(models.Model):
    _inherit = "op.assignment.sub.line"

    rubric_element_line = fields.One2many("op.assignment.rubric.sub.line",
                                          "assignment_sub_id",
                                          string="Rubrics Elements",
                                          required=True)
    state = fields.Selection(selection_add=[('to_assess', 'To Assess')])

    def act_to_assess(self):
        result = self.state = 'to_assess'

        if self.assignment_id.rubric_template_id:
            for element_line in self.assignment_id. \
                    rubric_template_id.rubric_element_line:
                if element_line.rubrics_type == 'points':
                    maximum = element_line.point
                elif element_line.rubrics_type == "percent":
                    maximum = element_line.percentage
                self.update({
                    'rubric_element_line': [(0, 0, {
                        'rubric_element_id': element_line.id,
                        'rubrics_type': element_line.rubrics_type,
                        'maximum': maximum
                    })],
                })
            return result and result or False

    def act_accept(self):
        result = self.state = 'accept'
        current_list = []
        for element_line in self.rubric_element_line:
            if element_line.rubrics_type == 'percent':
                initial_marks = self.assignment_id.point * element_line. \
                    rubric_element_id.percentage / 100
                final_marks = initial_marks * element_line.percentage / element_line. \
                    rubric_element_id.percentage
                current_list.append(final_marks)
            elif element_line.rubrics_type == 'points':
                current_list.append(element_line.point)
            self.update({
                'marks': sum(current_list)
            })
        return result and result or False


class OpAssignmentRubricSubline(models.Model):
    _name = "op.assignment.rubric.sub.line"
    _description = "Rubric Sub Line"

    rubric_element_id = fields.Many2one("op.rubric.element", "Element")
    assignment_sub_id = fields.Many2one("op.assignment.sub.line")
    marks = fields.Integer("Marks")
    rubrics_type = fields.Selection(
        [('no_points', 'No Points'),
         ('points', 'Points'),
         ('percent', 'Percent')],
        'Rubrics type', default="points",
        required=True)
    maximum = fields.Float("Out of")
    point = fields.Float("Point")
    percentage = fields.Float("Percentage")

    @api.onchange("point")
    def _point_error_raise(self):
        for rec in self:
            if rec.point:
                if rec.point > rec.rubric_element_id.point:
                    raise UserError(_('The given'
                                      ' point should'
                                      ' be less'
                                      ' than %s which'
                                      ' is assigned'
                                      ' for %s.') % (rec.rubric_element_id.point,
                                                     rec.rubric_element_id.name))

    @api.onchange("percentage")
    def _percentage_error_raise(self):
        for rec in self:
            if rec.percentage:
                if rec.percentage > rec.rubric_element_id.percentage:
                    raise UserError(_('The given'
                                      ' percentage should'
                                      ' be less'
                                      ' than %s which'
                                      ' is assigned'
                                      ' for %s.') % (rec.rubric_element_id.percentage,
                                                     rec.rubric_element_id.name))
