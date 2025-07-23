# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

import logging

from .test_progression_common import TestProgressionCommon


class TestProgression(TestProgressionCommon):

    def setUp(self):
        super(TestProgression, self).setUp()

    def test_case_1_progression(self):
        progressions = self.op_progression.search([])

        for progression in progressions:
            logging.info('Details of Core Company')
            logging.info('Name : %s :  ' % (progression.name))
            logging.info('student_id : %s :  ' % (progression.student_id))
            logging.info('created_by : %s :  ' % (progression.created_by))
            logging.info('date : %s :  ' % (progression.date))
            logging.info('state : %s :  ' % (progression.state))

        progressions.state_draft()
        progressions.state_open()
        progressions.state_done()
        progressions.state_rejected()
