# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import models


class OpQuizResult(models.Model):
    _inherit = "op.quiz.result"

    def get_answer_data(self):
        wrong_answers = []
        not_attempt_answer = []
        right_answers = []
        for line in self.line_ids:
            if not line.given_answer:
                not_attempt_answer.append({
                    'que_type': line.que_type, 'question': line.name,
                    'answer': line.answer or ''})
            elif line.answer == line.given_answer:
                right_answers.append({
                    'que_type': line.que_type, 'question': line.name,
                    'answer': line.answer})
            else:
                wrong_answers.append({
                    'que_type': line.que_type,
                    'question': line.name,
                    'given_answer': line.given_answer,
                    'answer': line.answer or '',
                })
        quiz = self.quiz_id
        display_wrong_ans = 0
        if quiz.wrong_ans and wrong_answers:
            display_wrong_ans = 1
        display_true_ans = 0
        if quiz.right_ans and right_answers:
            display_true_ans = 1
        not_attempt_ans = 0
        if quiz.not_attempt_ans and not_attempt_answer:
            not_attempt_ans = 1
        message = ''
        is_message = 0
        for msg in quiz.quiz_message_ids:
            result_to = msg.result_to
            result_from = msg.result_from
            if (self.score <= result_to) and (self.score >= result_from):
                message = msg.message
                is_message = 1
        return {
            'wrong_answer': wrong_answers,
            'not_attempt_answer': not_attempt_answer,
            'right_answers': right_answers,
            'total_question': self.total_question,
            'total_correct': self.total_correct,
            'total_incorrect': self.total_incorrect,
            'total_marks': self.total_marks,
            'received_marks': self.received_marks,
            'percentage': self.score,
            'display_wrong_ans': display_wrong_ans,
            'display_true_ans': display_true_ans,
            'not_attempt_ans': not_attempt_ans,
            'message': message,
            'is_message': is_message
        }
