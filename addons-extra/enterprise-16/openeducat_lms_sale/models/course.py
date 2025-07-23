# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import fields, models


class OpCourse(models.Model):
    _inherit = "op.course"

    type = fields.Selection([('free', 'Free'), ('paid', 'Paid')],
                            'Type', default='free')
    price = fields.Float('Price')
    product_id = fields.Many2one('product.product', 'Product',
                                 tracking=True)

    def action_confirm(self):
        if self.type == 'paid' and self.price and not self.product_id:
            product = self.env['product.product'].create(
                {'name': self.name,
                 'type': 'service',
                 'website_published': True,
                 'lst_price': self.price})
            self.product_id = product
        elif self.type == 'paid' and self.price and self.product_id:
            self.product_id.lst_price = self.price
        return super(OpCourse, self).action_confirm()
