# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

import logging

from .test_placement_job_common import TestPlacementJobCommon


class TestActivityAnnouncement(TestPlacementJobCommon):

    def setUp(self):
        super(TestActivityAnnouncement, self).setUp()

    def test_case_activity_announcement(self):
        types = self.op_activity_announcement.search([])
        for activity_announcement in types:
            logging.info('Name : %s' % activity_announcement.name)
            logging.info('code : %s' % activity_announcement.partner_id.name)
            for job_post in activity_announcement.job_post_id:
                logging.info('Job Post : %s' % job_post.name)
            for skill in activity_announcement.skill_id:
                logging.info('Skill Category : %s' % skill.name)
            logging.info('Track Subtype : %s'
                         % activity_announcement.
                         _track_subtype(activity_announcement.state))
            activity_announcement._compute_website_url()
            activity_announcement.set_draft()
            activity_announcement.set_open()
            activity_announcement.set_closed()


class TestJobApplicant(TestPlacementJobCommon):

    def setUp(self):
        super(TestJobApplicant, self).setUp()

    def test_case_job_applicant(self):
        types = self.op_job_applicant.search([])
        for job_applicant in types:
            logging.info('Name : %s' % job_applicant.activity_id.name)
