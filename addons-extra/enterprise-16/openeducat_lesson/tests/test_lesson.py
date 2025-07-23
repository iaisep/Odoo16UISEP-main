# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from logging import info

from .test_lesson_common import TestLessonCommon


class TestLesson(TestLessonCommon):

    def setUp(self):
        super(TestLesson, self).setUp()

    def test_case_lesson(self):
        lesson = self.op_lesson.search([])
        if not lesson:
            raise AssertionError(
                'Error in data, please check for Lesson Planning details')
        info('  Details Of Lesson Planning:.....')
        for record in lesson:
            info('      Lecture Name : %s' % record.name)
            info('      Course : %s' % record.course_id.name)
            info('      Batch : %s' % record.batch_id.name)
            info('      Subject : %s' % record.subject_id.name)
            info('      Lecture Topic : %s' % record.lesson_topic)
            info('      Faculty : %s' % record.faculty_id.name)
            info('      Start Time : %s' % record.start_datetime)
            info('      End Time : %s' % record.end_datetime)
            info('      Session : %s' % record.session_ids.name)
            info('      State : %s' % record.state)
            record.onchange_course_id()
            record.onchange_course()
            record.onchange_faculty_id()
            record.lesson_draft()
            record.lesson_plan()
            record.lesson_conduct()
            record.lesson_cancel()
