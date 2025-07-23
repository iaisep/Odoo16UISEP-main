# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from logging import info

from .test_timetable_common import TestTimetableCommon


class TestTimetable(TestTimetableCommon):

    def setUp(self):
        super(TestTimetable, self).setUp()

    def test_case_batch(self):
        batch = self.op_batch.search([])
        if not batch:
            raise AssertionError(
                'Error in data, please check for timetable report details')
        info('  Details Of timetable report:.....')
        for record in batch:
            record.open_generate_timetable()
            record.open_generate_timetable_reports()


class TestTimetableSession(TestTimetableCommon):

    def setUp(self):
        super(TestTimetableSession, self).setUp()

    def test_case_timetable_session(self):
        session = self.op_session.search([])
        if not session:
            raise AssertionError(
                'Error in data, please check for timetable session details')
        info('  Details Of Timetable Sessions:.....')
        for record in session:
            info('      Company : %s' % record.company_id.name)


class TestTimetableTiming(TestTimetableCommon):

    def setUp(self):
        super(TestTimetableTiming, self).setUp()

    def test_case_timetable_timimg(self):
        timing = self.op_timing.search([])
        if not timing:
            raise AssertionError(
                'Error in data, please check for timetable timing details')
        info('  Details Of Timetable Timings:.....')
        for record in timing:
            info('      Company : %s' % record.company_id.name)
            record.action_onboarding_timing_layout()


class TestTimetableOnboarding(TestTimetableCommon):

    def setUp(self):
        super(TestTimetableOnboarding, self).setUp()

    def test_case_timetable_onboarding_panel(self):
        company = self.op_company.search([])
        if not company:
            raise AssertionError(
                'Error in data, '
                'please check for timetable onboarding panel functions')
        info('  Timetable Onboarding Panel:.....')
        for record in company:
            record.action_close_timing_panel_onboarding()
            record.action_onboarding_timing_layout()
            record.update_timing_onboarding_state()
