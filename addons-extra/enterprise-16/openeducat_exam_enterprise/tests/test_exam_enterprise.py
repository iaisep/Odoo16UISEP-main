# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################
from .test_exam_common import TestExamCommon


class TestMarksheetLine(TestExamCommon):

    def setUp(self):
        super(TestMarksheetLine, self).setUp()

    def test_marksheet_line(self):
        line = self.op_marksheet_line.search([])
        for x in line:
            x.onchange_student_marksheet_line_progrssion()
            # x._compute_grand_total()

        marksheet_register = self.env['op.marksheet.register'].search([])
        data = marksheet_register.create({
            'name': 'Marksheet for BOA-Exam 2',
            'exam_session_id': 1,
            'generated_date': '2021-03-28',
            'generated_by': 2,
            'result_template_id': 1,
            'state': 'validated'
        })
        self.env['res.users'].search(
            [('login', '=', 'student@openeducat.com')])
        std = self.env['op.student'].search(
            [('email', '=', 'sumitasdani@demo.com')])
        marksheet_line = self.env['op.marksheet.line'].search([])
        data2 = marksheet_line.create({
            'marksheet_reg_id': data.id,
            'student_id': std.id
        })

        data2.search_read_for_result()


class TestResCompany(TestExamCommon):

    def setUp(self):
        super(TestResCompany, self).setUp()

    def test_res_company(self):
        company = self.res_company.search([])

        company.action_close_exam_panel_onboarding()
        company.action_onboarding_exam_layout()
        company.action_onboarding_exam_room_layout()
        company.action_onboarding_exam_grade_layout()
        company.update_exam_onboarding_state()


class TestExamSession(TestExamCommon):

    def setUp(self):
        super(TestExamSession, self).setUp()

    def test_exam_session(self):
        exam_session = self.op_exam_session.search([])
        data = exam_session.create({
            'name': 'Sumita',
            'course_id': 1,
            'batch_id': 1,
            'exam_code': 'BOA-E01',
            'start_date': "2021-02-21",
            'end_date': "2021-02-28",
            'exam_type': 1,
            'evaluation_type': 'normal',
            'venue': 1,


        })

        data.search_read_for_exam()
        for record in exam_session:
            record.search_read_for_exam()
