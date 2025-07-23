# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

import logging

from .test_alumni_common import TestAlumniCommon


class TestAlumniGroup(TestAlumniCommon):

    def setUp(self):
        super(TestAlumniGroup, self).setUp()

    def test_case_alumni_group(self):
        types = self.op_alumni_group.search([])
        if not types:
            raise AssertionError(
                'Error in data, please check for Alumni Group data')
        for alumni_group in types:
            logging.info('Name : %s' % alumni_group.name)
            alumni_group.createforum()


class TestAlumni(TestAlumniCommon):

    def setUp(self):
        super(TestAlumni, self).setUp()

    def test_case_alumni(self):
        types = self.op_alumni.search([], limit=1)
        for alumni in types:
            alumni.action_get_invoice()
