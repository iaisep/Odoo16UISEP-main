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


class TestLmsSaleCourseUpdate(TestLmsCommonSale):

    def test_2_paid_lsm_sale_course_update(self):
        data = self.env.ref('openeducat_lms_sale.demo_product')
        if not data or data.type != 'service':
            raise AssertionError(
                'Error in data, please check for '
                'demo data : openeducat_lms_sale.demo_product')
        logging.info('Product Details..... ')
        logging.info('Product Name  : %s' % data.name)
        logging.info('Product Type  : %s' % data.type)
        logging.info('Product Price : %d' % data.lst_price)
        course = self.env.ref('openeducat_lms.demo_course_2')
        if not course or course.type != 'paid':
            raise AssertionError(
                'Error in data, please check for '
                'demo data : openeducat_lms.demo_course_2')
        logging.info('Course Update with....')
        logging.info('Course Name     : %s' % course.name)
        logging.info('Course Type     : %s' % course.type)
        logging.info('Course Price    : %d' % course.price)
        logging.info('Course Product  : %s' % course.product_id.name)

    def test_2_free_lsm_sale_course_update(self):
        course = self.env.ref('openeducat_lms.demo_course_1')
        if not course or course.type != 'free':
            raise AssertionError(
                'Error in data, please check for '
                'demo data : openeducat_lms.demo_course_1')
        logging.info('Course Update with....')
        logging.info('Course Name     : %s' % course.name)
        logging.info('Course Type     : %s' % course.type)
