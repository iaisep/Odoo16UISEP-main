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


class TestLmsEnrollment(TestLmsCommonSale):

    def check_enrollment(self, enrollment, paid=False):
        logging.info('Details of Enrollment.....')
        logging.info('Course    : %s' % enrollment.course_id.name)
        logging.info('User      : %s' % enrollment.user_id.name)
        logging.info('State     : %s' % enrollment.state)
        if paid:
            logging.info('Order     : %s' % enrollment.order_id.name)
        logging.info('Navigation Policy : %s' % enrollment.navigation_policy)
        if not enrollment.enrollment_material_line:
            raise AssertionError(
                'Check for course material for : '
                '%s enrollment' % enrollment.course_id.name)
        logging.info('Details of material.....')
        for material in enrollment.enrollment_material_line:
            logging.info('  Material        : %s' % material.material_id.name)
            logging.info('  Is completed ?  : %s' % (
                'Yes' if material.completed else 'No'))

    # def test_4_enrollment_1(self):
    #     enrollment_1 = self.env.ref('openeducat_lms_sale.demo_enrollment_paid')
    #     if not enrollment_1:
    #         raise AssertionError(
    #             'Error in data, please check for '
    #             'demo data : openeducat_lms_sale.demo_enrollment_paid')
    #     self.check_enrollment(enrollment_1, paid=True)
    #
    #     enrollment_2 = self.env.ref('openeducat_lms_sale.demo_enrollment_free')
    #     if not enrollment_2:
    #         raise AssertionError(
    #             'Error in data, please check for '
    #             'demo data : openeducat_lms_sale.demo_enrollment_free')
    #     self.check_enrollment(enrollment_2)
