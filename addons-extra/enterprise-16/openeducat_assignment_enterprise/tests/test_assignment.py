# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from logging import info

from .test_assignment_common import TestAssignmentCommon


class TestOpAssignent(TestAssignmentCommon):

    def setUp(self):
        super(TestOpAssignent, self).setUp()

    def test_case_op_assignemnt(self):
        op_assignment = self.op_assignment.search([])

        for record in op_assignment:
            record.get_attempt()
            record.search_read_for_app()
            record.search_read_for_assignment_allocation()


class TestAssignmentSubline(TestAssignmentCommon):

    def setUp(self):
        super(TestAssignmentSubline, self).setUp()

    def test_case_assignment_subline(self):
        assignment_subline = self.op_assignment_subline.search([])
        for record in assignment_subline:
            info('      Assignment Name : %s' % record.assignment_id.id)
            info('      Student : %s' % record.student_id.id)
            info('      progression_id : %s' % record.progression_id.id)
            record.onchange_student_assignment_progrssion()
            record.ignore_submission_attempt()
            record.student_submission()
            record.search_read_for_app()


class TestAssignmentType(TestAssignmentCommon):

    def setUp(self):
        super(TestAssignmentType, self).setUp()

    def test_case_assignment_type(self):
        assignment_type = self.op_assignment_type.search([])
        if not assignment_type:
            raise AssertionError(
                'Error in data, please check for Activity type')
        info('Details of achievement_type')
        for category in assignment_type:
            info('      Assignment : %s' % category.name)
            category.action_onboarding_assignment_type_layout()


class TestProgressionAssignment(TestAssignmentCommon):

    def setUp(self):
        super(TestProgressionAssignment, self).setUp()

    def test_case_progression_assignment(self):
        progression_assignment = self.op_progression_assignment.search([])
        if not progression_assignment:
            raise AssertionError(
                'Error in data, please check for reference ')
        info('Details of Assignment')
        for record in progression_assignment:
            info('      Assignment : %s' %
                 record.assignment_lines.assignment_id.name)
            info('      Total Assignment Counts : %s' %
                 record.total_assignment)
            record._compute_total_assignment()


class TestCompany(TestAssignmentCommon):

    def setUp(self):
        super(TestCompany, self).setUp()

    def test_case_company(self):
        company = self.op_company.create({
            'name': "My Test Openeducat",
            'openeducat_assignment_onboard_panel': 'closed'})
        info('      test_case_company of TestCompany   %s ' % company.name)
        company.action_close_assignment_panel_onboarding
        company.action_onboarding_assignment_type_layout
        company.update_assignment_onboarding_state

    def test_case_1_progression_wizard(self):
        progression = self.op_progression_wizard.create({
            'student_id': self.env.ref('openeducat_core.op_student_1').id,
        })
        progression._get_default_student()
