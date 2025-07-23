# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

import logging

from .test_quiz_common import TestQuizCommon


class TestQuizGrade(TestQuizCommon):

    def setUp(self):
        super(TestQuizGrade, self).setUp()

    def test_case_2_quiz_grade(self):
        grades = self.op_grade.search([])
        if not grades:
            raise AssertionError(
                'Error in data, please check for Quiz Grades')
        logging.info('Details of quiz grades')
        logging.info('  Name     :   Grades(%)')
        for grade in grades:
            logging.info('%s :    %s' % (grade.name, grade.value))
