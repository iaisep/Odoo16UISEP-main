# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import fields, models


class OpQuestionWizard(models.TransientModel):
    _name = "op.question.wizard"
    _description = "Quiz Question Wizard"

    bank_id = fields.Many2one('op.question.bank', 'Question Bank')
    question_ids = fields.Many2many(
        'op.question.bank.line', string='Questions')

    def action_confirm_question(self):
        self.ensure_one()
        quiz = self.env['op.quiz'].browse(self.env.context.get('active_id'))
        que_ids = [x.que_id.id for x in quiz.line_ids if x.que_id]
        line_data = []
        for line in self.question_ids:
            if line.que_type in ['optional', 'blank', 'descriptive']:
                answer_data = []
                if line.id in que_ids:
                    continue
                for answer in line.line_ids:
                    answer_data.append([0, False, {
                        'name': answer.name,
                        'grade_id': answer.grade_id and answer.grade_id.id or False,
                    }])
                line_data.append([0, False, {
                    'name': line.name,
                    'mark': line.mark,
                    'que_id': line.id,
                    'que_type': line.que_type,
                    'line_ids': answer_data,
                    'answer': line.answer,
                    'grade_true_id': line.grade_true_id.id,
                    'grade_false_id': line.grade_false_id.id,
                    'material_type': line.material_type,
                    'video_type': line.video_type,
                    'url': line.url,
                    'datas': line.datas,
                    'document_id': line.document_id
                }])
        quiz.line_ids = line_data
        return self
