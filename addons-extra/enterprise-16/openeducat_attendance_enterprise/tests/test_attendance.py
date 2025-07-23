# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from logging import info

from .test_attendance_common import TestAttendanceCommon


class TestAttendanceLines(TestAttendanceCommon):

    def setUp(self):
        super(TestAttendanceLines, self).setUp()

    def test_attendance_line(self):
        line = self.op_attendance_line.search([])
        if not line:
            raise AssertionError(
                'Error in data, '
                'please check for Student Progression of Attendance')
        info('  Details Of Student Attendance Progression:.....')
        for record in line:
            record.onchange_student_attendance_progrssion()
            record.action_onboarding_attendance_lines_layout()


class TestAttendanceRegister(TestAttendanceCommon):

    def setUp(self):
        super(TestAttendanceRegister, self).setUp()

    def test_attendance_register(self):
        register = self.op_attendance_register.search([])
        if not register:
            raise AssertionError(
                'Error in data, please check for onboard function')
        for record in register:
            record.action_onboarding_attendance_register_layout()


class TestAttendanceSheet(TestAttendanceCommon):

    def setUp(self):
        super(TestAttendanceSheet, self).setUp()

    def test_attendance_sheet(self):
        sheet = self.op_attendance_sheet.search([])
        if not sheet:
            raise AssertionError(
                'Error in data, please check for onboard function')
        for record in sheet:
            record.action_onboarding_attendance_sheet_layout()
            record.attendance_sheet_daily()
            record.attendance_sheet_weekly()
            record.attendance_sheet_monthly()
            record.attendance_sheet_daily_if_session()


class TestBatch(TestAttendanceCommon):

    def setUp(self):
        super(TestBatch, self).setUp()

    def test_attendance_sheet_batch(self):
        batch = self.op_batch.search([])
        if not batch:
            raise AssertionError(
                'Error in data,'
                ' please check for attendance sheets details of batch')
        info('  Details Of Student Attendance Sheets:.....')
        for record in batch:
            record._compute_total_present()
            record._compute_total_absent()
            record._compute_kanban_dashboard_graph()
            record.create_attendance_sheet()
            record.get_bar_graph_datas()


class TestCompany(TestAttendanceCommon):

    def setUp(self):
        super(TestCompany, self).setUp()

    def test_attendance_sheet_onboard_panel(self):
        company = self.op_company.search([])
        if not company:
            raise AssertionError(
                'Error in data, please check for onboarding functions')
        info('  Attendance Onboard Panel:.....')
        for record in company:
            record.action_close_attendance_panel_onboarding()
            record.action_onboarding_attendance_register_layout()
            record.action_onboarding_attendance_sheet_layout()
            record.action_onboarding_attendance_lines_layout()
            record.update_attendance_onboarding_state()


class TestAttendanceProgression(TestAttendanceCommon):

    def setUp(self):
        super(TestAttendanceProgression, self).setUp()

    def test_attendance_progression(self):
        progression = self.op_progression.search([])
        if not progression:
            raise AssertionError(
                'Error in data, '
                'please check for attendance progression function')
        for record in progression:
            record._compute_total_attendance()
