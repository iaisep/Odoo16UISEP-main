# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################
from logging import info

from odoo.tests import common


class TestLmsForumCommon(common.TransactionCase):

    def setUp(self):
        super(TestLmsForumCommon, self).setUp()

    def test_lms_forum(self):
        cases = {
            '1': {
                'course': self.env.ref('openeducat_lms.demo_course_1'),
                'forum': self.env.ref(
                    'openeducat_lms_forum.demo_course_1_forum'),
                'post_1': self.env.ref('openeducat_lms_forum.forum_post_1'),
                'post_2': self.env.ref('openeducat_lms_forum.forum_post_2')
            },
            '2': {
                'course': self.env.ref('openeducat_lms.demo_course_2'),
                'forum': self.env.ref(
                    'openeducat_lms_forum.demo_course_2_forum'),
                'post_1': self.env.ref('openeducat_lms_forum.forum_post_3'),
                'post_2': self.env.ref('openeducat_lms_forum.forum_post_4')
            },
            '3': {
                'course': self.env.ref('openeducat_lms.demo_course_3'),
                'forum': self.env.ref(
                    'openeducat_lms_forum.demo_course_3_forum'),
                'post_1': self.env.ref('openeducat_lms_forum.forum_post_5'),
                'post_2': self.env.ref('openeducat_lms_forum.forum_post_6')
            }
        }

        for case in cases:
            self.details_of_forum(cases.get(case))

    def details_of_forum(self, data):
        course = data.get('course')
        forum = data.get('forum')
        post_1 = data.get('post_1')
        post_2 = data.get('post_2')

        if course.forum_id != forum:
            raise AssertionError(
                'Error in data, please check for forum in %s course' %
                course.name)
        info('Course : %s' % course.name)
        info('  Forum : %s' % forum.name)
        if post_1.forum_id != forum or post_2.forum_id != forum:
            raise AssertionError(
                'Error in data, please check for posts for %s forum' %
                forum.name)
        info('      Post-1 : %s' % post_1.name)
        info('      Post-2 : %s' % post_2.name)


class TestCourseForum(common.TransactionCase):

    def setUp(self):
        super(TestCourseForum, self).setUp()

    def test_op_course_forum(self):
        self.op_forum = self.env['op.course']

        course = self.op_forum.search([])
        course.action_create_forum()
