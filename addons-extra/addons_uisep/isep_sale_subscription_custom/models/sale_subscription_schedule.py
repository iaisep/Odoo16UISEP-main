from os import terminal_size
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.fields import Date
from datetime import datetime, date, timedelta
from collections import defaultdict
from odoo.tools import date_utils
from dateutil.relativedelta import relativedelta
from odoo.osv import expression
from odoo.tools import formatLang



class SaleSubscriptionPaymentSchedule(models.Model):
    _name = "sale.subscription.schedule"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Plazo de pagos"

    order_id = fields.Many2one(
        string="# Suscripción",
        comodel_name="sale.order",
        store=True,
        index=True,
    )

    term_number = fields.Integer('Nro. Plazo')
    term_label = fields.Char('Plazo')

    notification_date = fields.Date(
        string="Fecha de notificación",
    )
    date_due = fields.Date(
        string="Fecha de vencimiento",
        required=True,
    )

    date_schedule = fields.Date(
        string="Fecha",
        required=True,
    )


    date_executed = fields.Date(
        string="Fecha a ejecutar",
        compute="_compute_date_executed",
        store=True
    )

    payment_state = fields.Selection([('not_paid', 'Sin pagar'),('partial', 'Pagado parcialmente'),('paid', 'Pagado'),('cancel', 'Anulado')], 
        default="not_paid", 
        string="Estado", 
        compute="compute_payment_state", store=True, index=True)
    user_id = fields.Many2one('res.users',string="Responsable")
    name = fields.Char(string="Nombre", compute="_compute_ref_name", store=True, index=True)


    def action_open_order(self):
        self.ensure_one()
        if not self.order_id:
            raise UserError("No hay una orden vinculada a este registro.")
        return {
            'type': 'ir.actions.act_window',
            'name': 'Orden de Venta',
            'res_model': 'sale.order',
            'res_id': self.order_id.id,
            'view_mode': 'form',
            'target': 'current',
        }


    def open_full_view_term(self):
        self.ensure_one()
        result = self.env['ir.actions.act_window']._for_xml_id('isep_sale_subscription_custom.sale_subscription_schedule_action')
        result['views'] = [(self.env.ref('isep_sale_subscription_custom.sale_subscription_schedule_view_form', False).id, 'form')]
        result['res_id'] = self.id
        return result

    @api.model_create_multi
    def create(self, vals):
        record = super(SaleSubscriptionPaymentSchedule, self).create(vals)        
        if record.amount_recurring_taxinc <= 0:
            raise UserError('El Total a cobrar debe ser diferente de CERO.')
        return record

    

    @api.depends('total_paid')
    def compute_payment_state(self):
        for record in self:
            total_paid =round(record.total_paid,2)
            payment_state = 'not_paid'
            amount_recurring_taxinc = record.amount_recurring_taxinc
            if total_paid > 0 and total_paid < amount_recurring_taxinc:
                payment_state = 'partial'
            elif total_paid >= amount_recurring_taxinc:
                payment_state = 'paid'
            record.payment_state = payment_state

    

    @api.depends('order_id','term_label')
    def _compute_ref_name(self):
        for record in self:
            name = 'Nuevo'
            if record.order_id and record.term_label:
                name = '%s - Plazo %s' % (record.order_id.name, record.term_label)
            record.name = name

    
    
    currency_id = fields.Many2one(
        string="Moneda",
        comodel_name="res.currency",
        related="order_id.currency_id",
        store=True,
    )
    
    amount_recurring_taxinc = fields.Monetary(
        string="Total a cobrar",
        readonly=True
    )    

    company_id = fields.Many2one(
        string="Empresa",
        comodel_name="res.company",
        related="order_id.company_id",
        store=True,
        index=True,
    )
    
    stage_id = fields.Many2one(
        string="Etapa",
        comodel_name="sale.order.stage",
        related="order_id.stage_id",
        store=True,
        index=True,
    )    


    partner_id = fields.Many2one(
        string="Cliente",
        comodel_name="res.partner",
        related="order_id.partner_id",
        store=True,
        index=True,
    )
    
    partner_invoice_id = fields.Many2one(
        string="Facturado a",
        comodel_name="res.partner",
        related="order_id.partner_invoice_id",
        store=True,
        index=True,
    )

    invoice_ids = fields.One2many(
        'account.move', 'schedule_id',
        string="Facturas",
        domain=[('move_type', 'in', ['out_invoice', 'out_refund'])],
    )

    def action_aux_disassociate(self):
        invoices = self.invoice_ids.filtered(lambda inv: inv.aux_disassociate == True)
        for inv in invoices:
            inv.schedule_id = False
            inv.aux_disassociate = False

        

    def action_add_invoices(self):
        return {
            'name': 'Agregar Facturas',
            'type': 'ir.actions.act_window',
            'res_model': 'schedule.add.invoice.wizard',
            'view_mode': 'form',
            'target': 'new',
            'flags': {'action_buttons': False},      
            'context': {'default_partner_id': self.partner_id.id , 'default_partner_invoice_id': self.partner_invoice_id.id , 'default_currency_id': self.currency_id.id , },
            #'context': {'default_invoice_ids': [(6, 0, self.invoice_ids.ids)]},
        }
    
    

    """def action_add_invoices(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id("account.action_move_out_invoice_type")        
        action['domain'] = [('partner_id','in', (self.partner_id.id,self.partner_invoice_id.id)), ('state','=','posted'), ('currency_id','=',self.currency_id.id), ('schedule_id','=',False )  ]
        action['context'] = {}
        action['target'] = 'new'
        action['flags'] = {'action_buttons': False}
        return action"""
    


    """invoice_ids = fields.Many2many(
        string="Facturas",
        domain=[
            ('move_type', 'in', ['out_invoice', 'out_refund']),
            ('schedule_id', '=', False),
        ],
    )"""

    payment_legacy_ids = fields.One2many(
        'sale.note.inv.legacy', 'schedule_id',
        string="Otros pagos/facturas"
    )


    total_invoiced = fields.Monetary(
        compute='_compute_total_invoiced', 
        string='Total facturado',
        store=True
    )

    total_paid = fields.Monetary(
        compute='_compute_total_invoiced', 
        string='Total pagado',
        store=True
    )

    total_residual = fields.Monetary(
        compute='_compute_total_invoiced', 
        string='Total Pendiente',
        store=True
    )
    
    warning_ignore = fields.Boolean("Ignorar warning")
    warning_count = fields.Integer("Warning", compute="compute_warning_count", store=True, index=True)
    warning_msn = fields.Text("Warning Mensaje", compute="compute_warning_count", store=True, index=True)
    

    @api.depends('amount_recurring_taxinc','total_invoiced','invoice_ids.currency_id','warning_ignore')
    def compute_warning_count(self):
        for record in self:
            msn = []
            count = 0
            if not record.warning_ignore:
                if record.total_invoiced > record.amount_recurring_taxinc:
                    count+=1 
                    msn.append('** El total facturado excede el Total a cobrar.')
                if any(inv.currency_id != record.currency_id for inv in record.invoice_ids):             
                    count+=1 
                    msn.append('** La divisa/moneda son diferente.')
            record.warning_msn = '\n'.join(msn)
            record.warning_count = count



    note = fields.Html(string="Nota interna")

    # NOTE: SOLO SOPORTA UNA DIVISA, PENDIENTE MULTIDIVISA
    @api.depends('invoice_ids.amount_total','payment_legacy_ids.amount_total_invoice','invoice_ids.amount_residual','payment_legacy_ids.amount_total_payment')
    def _compute_total_invoiced(self):
        for schedule in self:
            schedule.total_invoiced = sum(schedule.invoice_ids.mapped('amount_total')) + sum(schedule.payment_legacy_ids.mapped('amount_total_invoice'))
            diff_invoice = round(schedule.amount_recurring_taxinc - schedule.total_invoiced , 2)
            
            schedule.total_residual = diff_invoice +  sum(schedule.invoice_ids.mapped('amount_residual')) + sum(schedule.payment_legacy_ids.mapped('amount_residual'))
            schedule.total_paid = schedule.amount_recurring_taxinc - schedule.total_residual

       


    def unlink(self):
        for record in self:

            if record.order_id:
                raise UserError(
                    "No se puede eliminar un registro con una suscripción vinculada (order_id)."
                )
            if record.invoice_ids or record.payment_legacy_ids:
                raise UserError(
                    "%s: No se puede eliminar un registro con facturas asociadas." % record.name
                )
            
            

        return super(SaleSubscriptionPaymentSchedule, self).unlink()

    

    def action_view_source_sale_order(self):
        self.ensure_one()
        source_orders = self.order_id
        result = self.env['ir.actions.act_window']._for_xml_id('sale.action_orders')
        result['views'] = [(self.env.ref('sale.view_order_form', False).id, 'form')]
        result['res_id'] = source_orders.id
        return result


    """
    def action_view_source_sale_orders(self):
        self.ensure_one()
        source_orders = self.line_ids.sale_line_ids.order_id
        result = self.env['ir.actions.act_window']._for_xml_id('sale.action_orders')
        if len(source_orders) > 1:
            result['domain'] = [('id', 'in', source_orders.ids)]
        elif len(source_orders) == 1:
            result['views'] = [(self.env.ref('sale.view_order_form', False).id, 'form')]
            result['res_id'] = source_orders.id
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result"""


    @api.model
    def read_grid(self, row_fields, col_field, cell_field, domain=None, range=None):
        # Filtro por defecto para estados no pagados
        self = self.with_context(prefetch_fields=True)
        default_domain = expression.AND([
            [('payment_state', 'in', ['not_paid', 'partial'])],
            [('date_due', '!=', False)],
            [('total_residual', '>', 0)]
        ])
        
        if domain:
            domain = expression.AND([domain, default_domain])
        else:
            domain = default_domain
            
        return super().read_grid(
            row_fields, 
            col_field, 
            cell_field, 
            domain=domain, 
            range=range
        )

    def action_open_invoices(self):
        self = self.sudo()
        self.ensure_one()
        
        # Forzar apertura de la orden
        return {
            'type': 'ir.actions.act_window',
            'name': 'Orden de Venta',
            'res_model': 'sale.order',
            'res_id': self.order_id.id,
            'view_mode': 'form',
            'target': 'current',
            'flags': {'action_buttons': True, 'headless': True},
        }


    
    token_exist = fields.Char(
        string="Tokens",
        compute="_compute_tokens",
        store=True
    )

    @api.depends('order_id.payment_token_id')
    def _compute_tokens(self):  
        for rec in self:
            tokens = rec.order_id.payment_token_id
            if not tokens:
                rec.token_exist = "Token: No"
            else:
                rec.token_exist = "Token: Si"	   

    total_recurring = fields.Char(
        string="Total a cobrar",
        compute="_compute_order_recurring_total",
        store=True
    )

    total_diff = fields.Char(
        string="Total diferencia",
        compute="_compute_order_diff_total",
        store=True
    )
    

    total_paid_new = fields.Char(
        string="Total pagos",
        compute="_compute_order_pagos_total",
        store=True
    )    

    @api.depends('order_id.total_recurring')
    def _compute_order_recurring_total(self):
        for rec in self:
            currency = rec.order_id.currency_id
            amount = rec.order_id.total_recurring or 0.0
            formatted_amount = formatLang(self.env, amount, currency_obj=currency)
            rec.total_recurring = f"Total cobro: {formatted_amount}"

    @api.depends('order_id.total_paid')
    def _compute_order_pagos_total(self):
        for rec in self:
            currency = rec.order_id.currency_id
            amount = rec.order_id.total_paid or 0.0
            formatted_amount = formatLang(self.env, amount, currency_obj=currency)
            rec.total_paid_new = f"Total pagos: {formatted_amount}"


    @api.depends('order_id.total_recurring', 'order_id.total_paid')
    def _compute_order_diff_total(self):
        for rec in self:
            currency = rec.order_id.currency_id
            # Asegurate que sean float o Decimal
            recurring = rec.order_id.total_recurring or 0.0
            paid = rec.order_id.total_paid or 0.0
            amount = recurring - paid
            formatted_amount = formatLang(self.env, amount, currency_obj=currency)
            rec.total_diff = f"Residual: {formatted_amount}"


