# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

import logging

from .test_quiz_common import TestQuizCommon


class TestQueBank(TestQuizCommon):

    def setUp(self):
        super(TestQueBank, self).setUp()

    def test_case_4_que_bank(self):
        banks = self.op_que_bank.search([])
        if not banks:
            raise AssertionError(
                'Error in data, please check for Question Bank')
        logging.info('Details of Question Bank')
        logging.info('Name  :       Type        :   #Questions')
        for bank in banks:
            lines = len(
                self.op_que_bank_line.search([('bank_id', '=', bank.id)]))
            if not lines:
                raise AssertionError(
                    'Error in data, please check '
                    'for number of questions for %s' % bank.name)
            logging.info('%s    : %s    : %d' % (
                bank.name, bank.bank_type_id.name, lines))


class TestQuestionWizard(TestQuizCommon):

    def setUp(self):
        super(TestQuestionWizard, self).setUp()

    def test_question_wizard(self):
        bank_id = self.env.ref('openeducat_quiz.op_qu_bnk_maths')
        que_line = self.env.ref('openeducat_quiz.op_math_q01')

        wizard = self.op_question_wizard.create({
            'bank_id': bank_id.id,
            'question_ids': [(6, 0, [que_line.id])],
        })
        for res in wizard:
            res.action_confirm_question()


class TestOpQuizResultLine(TestQuizCommon):

    def setUp(self):
        super(TestOpQuizResultLine, self).setUp()

    def test_Quiz_Result_Line(self):
        result = self.op_quiz_result_line.search([])
        for x in result:
            x.get_line_answer()
            x._onchange_mark()
