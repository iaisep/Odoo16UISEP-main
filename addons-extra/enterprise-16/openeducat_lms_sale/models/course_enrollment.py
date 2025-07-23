# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import fields, models


class OpCourseEnrollment(models.Model):
    _inherit = "op.course.enrollment"

    order_id = fields.Many2one('sale.order', 'Order')
