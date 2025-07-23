# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo.tests import common


class TestPlacementCommon(common.TransactionCase):
    def setUp(self):
        super(TestPlacementCommon, self).setUp()
        self.op_placement = self.env['op.placement.offer']
        self.op_placement_cell = self.env['op.placement.cell']
