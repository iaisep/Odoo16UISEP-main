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


class TestGamification(common.TransactionCase):
    def setUp(self):
        super(TestGamification, self).setUp()
        self.op_course = self.env['op.course']
        self.gmfc_challenge = self.env['gamification.challenge']
        self.gmfc_goal_def = self.env['gamification.goal.definition']
        self.gmfc_goal = self.env['gamification.goal']
        self.gmfc_challenge_line = self.env['gamification.challenge.line']

    def test_gamification(self):
        course = self.env.ref('openeducat_lms.demo_course_1')
        info('Gamification details for course : %s' % course.name)
        if not course.challenge_ids:
            raise AssertionError(
                'Error in data. Please check for gamification in course.')
        for challenge in course.challenge_ids:
            self.show_challenge(challenge)
            if not challenge.line_ids:
                raise AssertionError('Error in Data.'
                                     ' There is no any goal in the challenge.')
            self.show_goal(challenge.line_ids)

    def show_challenge(self, challenge):
        info('Details of challenge : %s ' % challenge.name)
        info('  Period : %s' % challenge.period)
        if not challenge.manager_id:
            raise AssertionError(
                'Error in data. Please check for Responsible person '
                'in your gamification challenge.')
        info('  Responsible : %s' % challenge.manager_id.name)
        info('  Visibility mode : %s' % challenge.visibility_mode)
        if not challenge.reward_id:
            raise AssertionError(
                'Error in data. Please check for Reward '
                'in your gamification challenge.')
        info('  Reward : %s' % challenge.reward_id.name)

    def show_goal(self, goals):
        info('  Details of goals of challenges : ')
        for goal in goals:
            info('      Goal : %s' % goal.name)
            info('      Target Value to Reach : %f' % goal.target_goal)
            info('      Goal Performance : %s' % goal.condition)
