# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

import logging

from .test_placement_common import TestPlacementCommon


class TestPlacement(TestPlacementCommon):

    def setUp(self):
        super(TestPlacement, self).setUp()

    def test_case_health(self):
        types = self.op_placement.search([])
        for placement in types:
            logging.info('Type : %s' % placement.name)
            logging.info('Student Name : %s' % placement.student_id.name)
            logging.info('Join Date : %s' % placement.join_date)
            logging.info('Offer Package : %s' % placement.offer_package)
            logging.info('Training Period : %s' % placement.training_period)
            placement.placement_offer()
            placement.placement_join()
            placement.confirm_rejected()
            placement.confirm_to_draft()
            placement.confirm_cancel()


class TestPlacementcell(TestPlacementCommon):

    def setUp(self):
        super(TestPlacementcell, self).setUp()

    def test_case_health(self):
        types = self.op_placement_cell.search([])
        for placement_cell in types:
            logging.info('Type : %s' % placement_cell.name)
            logging.info('Team Leader : %s' % placement_cell.user_id.name)
            logging.info('Members Name : %s' % placement_cell.member_ids.name)
