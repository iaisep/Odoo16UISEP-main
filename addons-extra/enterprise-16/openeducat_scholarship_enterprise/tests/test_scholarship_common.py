# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################
from odoo.tests import common


class TestScholarshipCommon(common.TransactionCase):
    def setUp(self):
        super(TestScholarshipCommon, self).setUp()
        self.op_scholarship = self.env['op.scholarship']
        self.op_scholarship_type = self.env['op.scholarship.type']
