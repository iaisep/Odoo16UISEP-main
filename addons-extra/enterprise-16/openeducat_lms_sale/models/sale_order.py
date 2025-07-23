# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for so in self:
            enrollments = self.env['op.course.enrollment'].sudo().search(
                [('order_id', '=', so.id)])
            if enrollments:
                for e in enrollments:
                    e.state = 'in_progress'
        return res
