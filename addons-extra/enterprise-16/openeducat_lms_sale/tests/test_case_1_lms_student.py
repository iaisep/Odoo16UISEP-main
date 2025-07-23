# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################
import logging

from .test_lms_sale_common import TestLmsCommonSale


class TestLmsStudent(TestLmsCommonSale):

    def test_1_student(self):
        data = self.env.ref(
            'openeducat_lms_sale.demo_student_partner')
        student = self.env.ref('openeducat_lms_sale.demo_student')
        if not data or data.company_type != 'person' or not student:
            raise AssertionError(
                'Error in data, please check for '
                'demo data : openeducat_lms_sale.demo_student_partner and '
                'openeducat_lms_sale.demo_student')
        logging.info('Student Name : %s' % data.name)
