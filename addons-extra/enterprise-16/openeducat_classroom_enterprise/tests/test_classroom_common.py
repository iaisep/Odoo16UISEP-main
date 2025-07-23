# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo.tests import common


class TestClassroomCommon(common.TransactionCase):
    def setUp(self):
        super(TestClassroomCommon, self).setUp()
        self.op_classroom = self.env['op.classroom']
        self.op_asset = self.env['op.asset']
