# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

import logging

from .test_quiz_common import TestQuizCommon


class TestQuiz(TestQuizCommon):

    def setUp(self):
        super(TestQuiz, self).setUp()

    def check_data(self, msg, first_value, quiz_ref):
        if first_value != self.env.ref(quiz_ref):
            raise AssertionError(
                'Error in data, please check %s for referenced: '
                '%s' % (msg, quiz_ref))

    def check_config(self, quiz_config):
        config_list = ['normal', 'quiz_bank_selected', 'quiz_bank_random']
        if quiz_config not in config_list:
            raise AssertionError(
                'Error in data, %s is not valid please check Configuration '
                'for reference : openeducat_quiz.op_qz_1' % quiz_config)

    def test_case_4_quiz_1(self):
        quiz = self.env.ref('openeducat_quiz.op_qz_1')
        if not quiz:
            raise AssertionError(
                'Error in data, please check for reference : '
                'openeducat_quiz.op_qz_1')
        info = logging.info
        info('Details of Quiz :: %s' % quiz.name)
        self.check_data('Category', quiz.categ_id,
                        'openeducat_quiz.op_qz_ctg_1')
        info('Category : %s' % quiz.categ_id.name)
        self.check_config(quiz.quiz_config)
        info('Confguration: %s' % quiz.quiz_config)

    def test_case_4_quiz_2(self):
        quiz = self.env.ref('openeducat_quiz.op_qz_2')
        if not quiz:
            raise AssertionError(
                'Error in data, please check for reference : '
                'openeducat_quiz.op_qz_1')
        info = logging.info
        info('Details of Quiz :: %s' % quiz.name)
        self.check_data('Category', quiz.categ_id,
                        'openeducat_quiz.op_qz_ctg_2')
        info('Category : %s' % quiz.categ_id.name)
        self.check_config(quiz.quiz_config)
        info('Confguration: %s' % quiz.quiz_config)


class TestQuizOnboard(TestQuizCommon):

    def setUp(self):
        super(TestQuizOnboard, self).setUp()

    def test_quiz_onboard(self):
        quiz = self.quiz_onboard.search([])

        quiz.action_close_quiz_panel_onboarding()
        quiz.action_onboarding_quiz_layout()
        quiz.action_onboarding_question_bank_layout()
        quiz.update_quiz_onboarding_state()
