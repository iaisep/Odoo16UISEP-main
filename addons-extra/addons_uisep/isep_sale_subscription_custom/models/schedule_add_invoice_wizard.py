from odoo import api, fields, models

class ScheduleAddInvoiceWizard(models.TransientModel):
    _name = 'schedule.add.invoice.wizard'
    _description = 'Asistente para agregar facturas'

    invoice_ids = fields.Many2many('account.move', string='Facturas a agregar', domain=[('move_type', 'in', ['out_invoice', 'out_refund']), ('schedule_id', '=', False)]) 
    currency_id = fields.Many2one(
        string="Moneda",
        comodel_name="res.currency",
    )
    
    partner_id = fields.Many2one(
        string="Cliente",
        comodel_name="res.partner",
    )
    
    partner_invoice_id = fields.Many2one(
        string="Facturado a",
        comodel_name="res.partner",
    )

    def add_invoices(self):
        active_id = self.env.context.get('active_id')
        schedule = self.env['sale.subscription.schedule'].browse(active_id)
        for invoice in self.invoice_ids:
            invoice.schedule_id = schedule.id
            invoice.order_subscription_id = schedule.order_id
