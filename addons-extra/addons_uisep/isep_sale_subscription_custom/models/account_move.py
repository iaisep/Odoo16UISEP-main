import logging
from odoo import models, fields, api
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'


    schedule_id = fields.Many2one(
        string="Plazo en cronograma",
        comodel_name="sale.subscription.schedule",        
        ondelete='set null'
    )

    order_subscription_id = fields.Many2one(
        string="Suscripción",
        comodel_name="sale.order",
    )
    aux_disassociate = fields.Boolean('Desvincular')
    
    

    """def unlink(self):
        for record in self:
            if record.schedule_id or record.order_subscription_id:
                record.schedule_id = False
                record.order_subscription_id = False
        return super(AccountMove, self).unlink()"""

    
    def open_full_view_invoice(self):
        self.ensure_one()
        result = self.env['ir.actions.act_window']._for_xml_id('account.action_move_out_invoice_type')
        result['views'] = [(self.env.ref('account.view_move_form', False).id, 'form')]
        result['res_id'] = self.id
        return result



    def search_order_schedule_id(self, order):
        self.ensure_one()
        subscription_schedule = order.subscription_schedule
        #raise UserError(str(subscription_schedule))
        for lsc in subscription_schedule.filtered(lambda x: x.payment_state in ('not_paid','partial')):

            amount_recurring_taxinc =  lsc.amount_recurring_taxinc
            total_invoiced = lsc.total_invoiced
            if total_invoiced <= amount_recurring_taxinc:
                invoiced_pending = amount_recurring_taxinc - total_invoiced
                if self.amount_total <= invoiced_pending:
                    self.schedule_id = lsc.id
                    break
            
        if not self.schedule_id:
            order.write({
                'invoice_warning_ids': [(4, self.id)]
            })

            #breakterm_number


    def search_order_subscription_id(self):
        self.ensure_one()
        source_orders = self.line_ids.sale_line_ids.order_id
        if source_orders:
            for order in source_orders:
                self.order_subscription_id = order.id
                break
    
    @api.model_create_multi
    def create(self, vals):
        record = super(AccountMove, self).create(vals)
        if record:
            record.search_order_subscription_id()
            if record.order_subscription_id and not record.schedule_id:
                record.search_order_schedule_id(record.order_subscription_id)
        return record

    """def write(self, vals):
        res = super(AccountMove, self).write(vals)
        for record in self:
            if not record.order_subscription_id:
                record.search_order_subscription_id()
            if record.order_subscription_id and not record.schedule_id:
                record.search_order_schedule_id(record.order_subscription_id)
        return res"""