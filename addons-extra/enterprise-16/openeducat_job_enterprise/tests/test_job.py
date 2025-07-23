# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################


from .test_job_common import TestJobCommon


class TestJob(TestJobCommon):

    def setUp(self):
        super(TestJob, self).setUp()

    def test_case_job(self):
        types = self.op_job.search([])
        for job in types:
            job.check_dates()
            job._compute_application_count()
            job._compute_new_application_count()
            job._get_first_stage()
            job._compute_website_url()
            job.set_recruit()
            job.set_draft()
            job.set_review()
            job.set_submit()
            job.set_done()
            job.set_cancel()


class TestJobApplicant(TestJobCommon):

    def setUp(self):
        super(TestJobApplicant, self).setUp()

    def test_case_job_applicant(self):
        types = self.op_job_applicant.search([])
        for job_applicant in types:
            job_applicant._default_stage_id()
            job_applicant.onchange_post_id()
            job_applicant.onchange_stage_id()
            job_applicant._compute_day()
            job_applicant._compute_get_attachment_number()
            job_applicant.action_get_attachment_tree_view()


class TestJobStage(TestJobCommon):

    def setUp(self):
        super(TestJobStage, self).setUp()

    def test_case_job_stage(self):
        types = self.op_job_stage.search([])
        for job_stage in types:
            job_stage.default_get(fields="")
