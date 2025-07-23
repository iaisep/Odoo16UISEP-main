from odoo import api, fields, models
from datetime import timedelta,datetime
from dateutil.relativedelta import relativedelta

class ScheduleDateDueLine(models.TransientModel):
    _name = 'schedule.date.due.line'

    
    name = fields.Many2one(
        string="Plazo",
        comodel_name="sale.subscription.schedule",
    )

    
    currency_id = fields.Many2one(
        string="Moneda",
        comodel_name="res.currency"
    )
    

    total_paid = fields.Monetary(
        string='Total pagado',
    )


    total_residual = fields.Monetary(
        string='Total Pendiente',
    )


    payment_state = fields.Selection([('not_paid', 'Sin pagar'),('partial', 'Pagado parcialmente'),('paid', 'Pagado'),('cancel', 'Anulado')], 
        string="Estado")



    schedule_date_due_id = fields.Many2one(
        string="schedule due id",
        comodel_name="schedule.date.due",
    )

    date_due = fields.Date(
        string="Vencimiento",
        required=True,
    )

    new_date_due = fields.Date(
        string="Nueva Vencimiento",
        required=True,
    )
    exclude = fields.Boolean('Excluir')


class ScheduleDateDue(models.TransientModel):
    _name = 'schedule.date.due'
    _description = 'Prorrogar fechas'   
    
    order_id = fields.Many2one(
        string="Order",
        comodel_name="sale.order",
    )

    end_date = fields.Date(
        string="Fecha final (hasta)",
        required=True,
    )

    next_invoice_date = fields.Date(
        string="Siguiente Factura",
        required=True,
    )

    new_end_date = fields.Date(
        string="Nuevo: Fecha final",
        compute="_compute_new_end_date"
    )
    
    new_next_invoice_date = fields.Date(
        string="Nuevo: Siguiente Factura",
        required=True,
    )

    recurrence_id = fields.Many2one(
        string="Recurrencia",
        comodel_name="sale.temporal.recurrence",
    )
    
    
    

    schedule_due_line_ids = fields.One2many('schedule.date.due.line', 'schedule_date_due_id', string="Plazos a prorrogar")
    
    @api.onchange('new_next_invoice_date')
    def onchange_new_next_invoice_date(self):
        for record in self:
            period = relativedelta()
            unit = record.recurrence_id.unit
            duration = record.recurrence_id.duration
            current_multiplier = 0
            for line in record.schedule_due_line_ids.filtered(lambda x: x.exclude == False):
                adjusted_duration = duration * current_multiplier

                if unit == 'month':
                    period = relativedelta(months=adjusted_duration)
                elif unit == 'day':
                    period = relativedelta(days=adjusted_duration)
                elif unit == 'week':
                    period = relativedelta(weeks=adjusted_duration)
                elif unit == 'year':
                    period = relativedelta(years=adjusted_duration)

                line.new_date_due = record.new_next_invoice_date + period
                current_multiplier += 1

    @api.depends('schedule_due_line_ids.new_date_due')
    def _compute_new_end_date(self):
        for record in self:
            if record.schedule_due_line_ids:
                # Encuentra el new_date_due más lejano
                max_date = max(line.new_date_due for line in record.schedule_due_line_ids if line.new_date_due)
                if max_date:
                    record.new_end_date = max_date - timedelta(days=1)
                else:
                    record.new_end_date = False
            else:
                record.new_end_date = False
    # ok
    def update_date_due(self):
        for line in self.schedule_due_line_ids:
            line.name.date_due = line.new_date_due        
        self.order_id.next_invoice_date = self.new_next_invoice_date
        self.order_id.end_date = self.new_end_date
        
