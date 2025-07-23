# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################
from odoo.tests import common


class TestLmsCommonSale(common.TransactionCase):
    def setUp(self):
        super(TestLmsCommonSale, self).setUp()
        self.op_course = self.env['op.course']
        self.op_material = self.env['op.material']
        self.op_enrollment = self.env['op.course.enrollment']
        self.op_sale_order = self.env['sale.order']
