# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from logging import info

from .test_scholarship_common import TestScholarshipCommon


class TestScholarship(TestScholarshipCommon):

    def setUp(self):
        super(TestScholarship, self).setUp()

    def test_case_scholarship(self):
        scholarship = self.op_scholarship.search([])
        if not scholarship:
            raise AssertionError(
                'Error in data, please check for scholarship details')
        info('  Details Of Scholarship:.....')
        for record in scholarship:
            info('      Name : %s' % record.name)
            info('      Student : %s' % record.student_id.name)
            info('      Type : %s' % record.type_id.name)
            info('      Company : %s' % record.company_id.name)
            info('      Stages : %s' % record.scholarship_stages_id.name)


class TestScholarshipType(TestScholarshipCommon):
    def setUp(self):
        super(TestScholarshipType, self).setUp()

    def test_case_scholarship_type(self):
        scholarshiptype = self.op_scholarship_type.search([])
        if not scholarshiptype:
            raise AssertionError(
                'Error in data, please check for scholarship type details')
        info('  Details Of Scholarship Type:.....')
        for record in scholarshiptype:
            info('      Name : %s' % record.name)
            info('      Amount : %s' % record.amount)
            info('      Company : %s' % record.company_id.name)
            record.check_amount()
