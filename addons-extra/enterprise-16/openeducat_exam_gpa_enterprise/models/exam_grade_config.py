# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import api, fields, models


class ResultRecords(models.Model):

    _inherit = 'op.result.line'

    grade_point = fields.Float("Grade Point")
    credit = fields.Float(
        'Subject Credit', related='exam_id.subject_id.subject_credit')
    qp = fields.Float('Quality Points', compute="_compute_qp")

    @api.depends('grade_point', 'credit')
    def _compute_qp(self):
        ob_grade = self.env['op.grade.configuration'].search([])
        ob_marsheet_line = self.env['op.marksheet.line'].search([])

        for record in self:
            for data in ob_grade:
                if data.result == record.grade:
                    record.grade_point = data.grade_point

        for record in self:
            if record.grade_point:
                record.qp = record.grade_point * record.credit
            else:
                record.qp = False

        for record in ob_marsheet_line:
            record.total_points = sum([
                float(x.qp) for x in record.result_line])

        for record in ob_marsheet_line:
            total_credit = sum([float(x.credit)
                                for x in record.result_line])

            if record.total_points or total_credit > 0:
                record.gpa_count = record.total_points/total_credit


class OpeneducatMarksheetLineGpa(models.Model):

    _inherit = 'op.marksheet.line'

    gpa_count = fields.Float(
        "GPA", compute='_compute_gpa')

    total_points = fields.Float(
        "total_points")

    @api.depends('result_line.qp', 'total_points')
    def _compute_gpa(self):
        for record in self:
            record.total_points = sum([
                float(x.qp) for x in record.result_line])
        for record in self:
            total_credit = sum([float(x.credit)
                                for x in record.result_line])

            if record.total_points or total_credit > 0:
                record.gpa_count = record.total_points/total_credit
            else:
                record.gpa_count = False


class OpenducatSubjectCredit(models.Model):

    _inherit = 'op.subject'

    subject_credit = fields.Float("Credit Hours", default="5")


class OpenducatGradeConfig(models.Model):

    _inherit = 'op.grade.configuration'

    grade_point = fields.Float("Grade Point")
