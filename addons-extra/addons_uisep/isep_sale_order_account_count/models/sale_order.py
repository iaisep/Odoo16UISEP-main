# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime

_logger = logging.getLogger(__name__)


class SaleOrderAccountMoveCount(models.Model):
    _inherit = 'sale.order'

    overdue_invoice_count_s = fields.Integer(string="Facturas Vencidas")



    def calculate_overdue_invoices(self):
        today = fields.Date.today()
        for order in self:
            overdue_invoices = order.invoice_ids.filtered(
                lambda inv: inv.state == 'posted' and inv.invoice_date_due < today and inv.amount_residual > 0
            )
            order.overdue_invoice_count_s = len(overdue_invoices)


    
    def update_overdue_invoice_count_s(self):
        # Buscar todos los pedidos de venta
        sale_orders = self.search([('state','=', 'sale')])
        # Ejecutar el cálculo de facturas vencidas para cada pedido
        sale_orders.calculate_overdue_invoices()


    


