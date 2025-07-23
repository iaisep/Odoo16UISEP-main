# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from datetime import datetime

from .test_noticeboard_common import TestNoticeBoardCommon


class TestNoticeBoard(TestNoticeBoardCommon):
    def setUp(self):
        super(TestNoticeBoard, self).setUp()

    def test_01_noticeboard_group(self):
        notice_groups = self.op_notice_group.search([])
        for group in notice_groups:
            if group.all_students or group.selected_students:
                group._compute_target_student_audience()
            if group.all_parents or group.selected_parents:
                group._compute_target_parent_audience()
            if group.all_faculty or group.selected_faculty:
                group._compute_target_faculty_audience()

        group_data = {
            'name': 'Demo Group',
            'all_students': True,
            'course_ids': [self.ref('openeducat_core.op_course_2'),
                           self.ref('openeducat_core.op_course_3')],
            'batch_ids': [self.ref('openeducat_core.op_batch_1'),
                          self.ref('openeducat_core.op_batch_2')],
            'all_parents': True,
            'parent_course_ids': [self.ref('openeducat_core.op_course_2')],
            'parent_batch_ids': [self.ref('openeducat_core.op_batch_1')],
            'selected_faculty': True,
            'faculty_ids': [self.ref('openeducat_core.op_faculty_1'),
                            self.ref('openeducat_core.op_faculty_2')]
        }
        demo_group = self.op_notice_group.create(group_data)

        if demo_group.all_students or demo_group.selected_students:
            demo_group._compute_target_student_audience()
        if demo_group.all_parents or demo_group.selected_parents:
            demo_group._compute_target_parent_audience()
        if demo_group.all_faculty or demo_group.selected_faculty:
            demo_group._compute_target_faculty_audience()

        demo_group.update({
            'parent_course_ids': [self.ref('openeducat_core.op_course_2'),
                                  self.ref('openeducat_core.op_course_3')],
            'parent_batch_ids': [self.ref('openeducat_core.op_batch_1'),
                                 self.ref('openeducat_core.op_batch_2')],
        })
        demo_group._compute_target_parent_audience()

    def test_02_test_notice(self):
        all_notice = self.op_notice.search([])
        for notice in all_notice:
            if notice.state == 'publish':
                # notice.action_send_email()
                notice.action_to_unpublish()
            if notice.state == 'in_progress':
                notice.action_to_cancel()

        notice_data = {
            'name': 'Demo Notice',
            'subject': 'Demo Notice Subject',
            'group_id': self.ref('openeducat_notice_board_enterprise.notice_group1'),
            'start_date': datetime.today().date(),
            'academic_year_id': self.ref('openeducat_core.academic_year_3'),
            'academic_term_id': self.ref('openeducat_core.academic_term_1'),
            'description': 'Description for Demo Notice.'
        }

        demo_notice = self.op_notice.create(notice_data)

        demo_notice.action_to_in_progress()
        demo_notice.action_to_publish()
        # demo_notice.action_send_email()
        demo_notice.action_to_unpublish()

    def test_02_test_circular(self):
        all_circular = self.op_circular.search([])
        for circular in all_circular:
            if circular.state == 'publish':
                circular.circular_action_send_email()
                circular.action_unpublish()
            if circular.state == 'in_progress':
                circular.action_cancel()

        circular_data = {
            'name': 'Demo Circular',
            'subject': 'Demo Circular Subject',
            'group_id': self.ref('openeducat_notice_board_enterprise.notice_group1'),
            'start_date': datetime.today().date(),
            'academic_year_id': self.ref('openeducat_core.academic_year_3'),
            'academic_term_id': self.ref('openeducat_core.academic_term_1'),
            'description': 'Description for Demo Circular.'
        }

        demo_circular = self.op_circular.create(circular_data)

        demo_circular.action_in_progress()
        demo_circular.action_publish()
        demo_circular.circular_action_send_email()
        demo_circular.action_unpublish()
