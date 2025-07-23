# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from logging import info

from .test_meeting_common import TestMeetingCommon


class TestMeeting(TestMeetingCommon):

    def setUp(self):
        super(TestMeeting, self).setUp()

    def test_case_meeting_1(self):
        meeting = self.op_meeting.create({
            'name': "about meeting",
            'start': '2017-07-12 14:30:00',
            'allday': False,
            'rrule': u'FREQ=WEEKLY;BYDAY=WE;INTERVAL=1;COUNT=100',
            'duration': 0.5,
            'stop': '2017-07-12 15:00:00',
        })
        self.assertEqual(
            (str(meeting.start), str(meeting.stop)),
            (u'2017-07-12 14:30:00', u'2017-07-12 15:00:00'),
            "Sanity check"
        )
        self.assertEqual(
            (str(meeting.start), str(meeting.stop)),
            ('2017-07-12 14:30:00', u'2017-07-12 15:00:00'),
        )
        if not meeting:
            raise AssertionError(
                'Error in data, please check for reference Meeting')
        # meeting._inverse_dates()
        meeting.unlink()

    def test_case_meeting_2(self):
        meeting1 = self.op_meeting.search([])
        if not meeting1:
            raise AssertionError(
                'Error in data, please check for reference Meeting')
        info('Details of Meeting')
        for record in meeting1:
            info('      Meeting : %s' % record.meeting_id.name)
            info('      Start Date : %s' % record.start)

    def test_case_meeting_3(self):
        partner_id1 = self.env.ref('openeducat_core.op_res_partner_1')
        partner_id2 = self.env.ref('openeducat_core.op_res_partner_26')
        partner_id3 = self.env.ref('openeducat_parent.res_partner_33')
        faculty = self.env[('op.faculty')].search([
            ('partner_id', '=', partner_id2.id)])
        partner_ids = [partner_id1.id, faculty.id, partner_id3.id]
        meeting3 = self.op_meeting.create({
            'name': "Result Meeting",
            'start': '2017-07-12 14:30:00',
            'allday': True,
            'rrule': u'FREQ=WEEKLY;BYDAY=WE;INTERVAL=1;COUNT=100',
            'duration': 0.5,
            'stop': '2017-07-12 15:00:00',
            'partner_ids':  [(6, 0, partner_ids)]})
        meeting3.unlink()
