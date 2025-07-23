import logging
from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)



class SaleNoteInv(models.Model):
    _name = 'sale.note.inv'
    _description = 'Informacion de facturas de Odoo 12' 

    name = fields.Char(string="Referencia")
    order_id = fields.Many2one('sale.order', string="Venta", ondelete='cascade' )
    note = fields.Text(string="Nota")
    currency_id = fields.Many2one('res.currency', related="order_id.currency_id", string="Moneda")
    type = fields.Selection([
        ('invoice', 'Factura'),
        ('others', 'Otros'),
        ], required=True, default="invoice", string="Tipo")
    
    amount_total_invoice = fields.Monetary(string="Total Facturado")
    amount_total_payment = fields.Monetary(string="Total Pagado")


class SaleNoteInvLegacy(models.Model):
    _name = 'sale.note.inv.legacy'
    _description = 'Informacion de facturas de Odoo 12.' 

    
    name = fields.Char(string="Referencia")    
    schedule_id = fields.Many2one('sale.subscription.schedule', string="Plazo de pago", ondelete='cascade' ) 
    note = fields.Text(string="Nota")
    currency_id = fields.Many2one('res.currency', related="schedule_id.currency_id", string="Moneda")    
    invoice_date = fields.Date(string="Fecha de Factura")
    amount_total_invoice = fields.Monetary(string="Total Facturado")
    payment_date = fields.Date(string="Fecha de pago")
    amount_total_payment = fields.Monetary(string="Total Pagado")

    payment_state = fields.Selection([('not_paid', 'Sin pagar'),('partial', 'Pagado parcialmente'),('paid', 'Pagado'),('cancel', 'Anulado')], 
        default="not_paid", 
        string="Estado", 
        compute="_compute_payment_state", store=True, index=True)

    amount_residual = fields.Monetary(string="Saldo pendiente", compute='_compute_amount_residual', store=True)


    @api.depends('amount_total_invoice', 'amount_total_payment')
    def _compute_amount_residual(self):
        for record in self:
            record.amount_residual = record.amount_total_invoice - record.amount_total_payment
    
    @api.depends('amount_total_invoice', 'amount_total_payment')
    def _compute_payment_state(self):
        for record in self:
            if record.amount_total_invoice == 0:
                record.payment_state = 'paid'
            elif record.amount_total_payment == 0:
                record.payment_state = 'not_paid'
            elif record.amount_total_payment >= record.amount_total_invoice:
                record.payment_state = 'paid'
            elif record.amount_total_payment < record.amount_total_invoice:
                record.payment_state = 'partial'
            else:
                record.payment_state = 'not_paid'
    
    @api.constrains('amount_total_invoice', 'amount_total_payment')
    def _check_amounts(self):
        for record in self:
            if record.amount_total_invoice <= 0:
                raise UserError("El total de la factura debe ser mayor que cero.")
            if record.amount_total_payment > record.amount_total_invoice:
                raise UserError("El monto pagado no puede exceder el total de la factura.")