# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################
import logging

from .test_lms_sale_common import TestLmsCommonSale


class TestLmsSaleOrder(TestLmsCommonSale):

    def test_3_sale_order(self):
        so = self.env.ref('openeducat_lms_sale.demo_sale_order')
        if not so:
            raise AssertionError(
                'Error in data, please check for '
                'demo data : openeducat_lms_sale.demo_sale_order')

        logging.info('Details of Sale Order.....')
        logging.info('Order Name    : %s' % so.name)
        logging.info('Cutomer Name  : %s' % so.partner_id.name)
        logging.info('State         : %s' % so.state)
        if not so.order_line:
            raise AssertionError('Check Sale Order Line')
        logging.info('Details Of Sale Order Lines.....')
        logging.info('  Product Name  : %s' % so.order_line[0].product_id.name)
        logging.info('  Product Price : %s' % so.order_line[0].price_unit)


class TestOpSaleOrder(TestLmsCommonSale):

    def setUp(self):
        super(TestOpSaleOrder, self).setUp()

    def test_op_sale_order(self):
        sale = self.op_sale_order.search([], limit=1)
        sale.action_confirm()
        logging.info('sale_order-------')
