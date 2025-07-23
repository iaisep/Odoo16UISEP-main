# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

import logging

from .test_quiz_common import TestQuizCommon


class TestQueBankType(TestQuizCommon):

    def setUp(self):
        super(TestQueBankType, self).setUp()

    def test_case_3_que_bank_type(self):
        types = self.op_que_bank_type.search([])
        if not types:
            raise AssertionError(
                'Error in data, please check for Question Bank types')
        logging.info('Details of Question Bank Types')
        logging.info('Name  ::')
        for data in types:
            logging.info('%s' % data.name)
