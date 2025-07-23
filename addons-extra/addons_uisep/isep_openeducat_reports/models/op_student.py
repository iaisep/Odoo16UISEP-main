# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class OpStudent(models.Model):
    _inherit = "op.student"

    
    course_val = fields.Boolean(string= 'Validación de Curso', compute="_compute_validations")
    practice_val = fields.Boolean(string= 'Validación de Prácticas', compute="_compute_validations")
    payments_val = fields.Boolean(string= 'Validación de Cobranza', compute="_compute_validations")
    graduated_val = fields.Boolean(string= 'Finalizó la modalidad de titulación')
    discoursed_val = fields.Boolean(string= 'Disertó')

    

    def _compute_validations(self):
        for record in self:
            #Validacion de Curso
            courses = self.env['app.gradebook.student'].search([('student_id','=',record.id)])
            record.course_val = courses and all([gradebook.state == 'done' for gradebook in courses]) or False
            #Validacion de Prácticas
            practices = self.env['practice.request'].search([('user_id','=',record.user_id.id)])
            record.practice_val = practices and all([practice.state == 'end' for practice in practices]) or False
            #Validacion de Pagos en Suscripcion
            subscription_data = record.get_subscription_data()
            sale_order_ids = subscription_data.get('sale_order_ids', False)
            t_amount_due_data = subscription_data.get('t_amount_due_data', 0.0)
            t_adeuda = subscription_data.get('t_adeuda')
            record.payments_val = sale_order_ids and (not t_adeuda) and (t_amount_due_data <= 0) or False



 
    def get_subscription_data(self):
        self.ensure_one()  # Ensure this method is called on a single record
        res = {
                't_term_number': 0, # ok
                't_amount_recurring_due': 0.0, # ok
                't_amount_total_payment': 0.0, # ok
                't_amount_total': 0.0, # ok
                't_amount_recurring_taxinc': 0.0, # ok
                't_amount_no_recurring_taxinc': 0.0, # ok
                'currency_id': self.env.company.currency_id.sudo(),
                'sale_order_ids': self.env['sale.order'].sudo(),
                't_adeuda': False, # ok
              }
        sale_orders = self.env['sale.order'].sudo().search([('is_subscription','=',True),('partner_id','=',self.partner_id.id),('state','in',['sale','done'])])
        res['currency_id'] = sale_orders and sale_orders[0].currency_id or res['currency_id']
        res['sale_order_ids'] = sale_orders
        res['t_amount_due_total'] = sum([s.amount_due_total for s in sale_orders])
        for subscription in sale_orders:

            today = fields.Date.today()
            due_schedules = subscription.subscription_schedule.filtered(lambda s: s.date_due <= today)
            t_amount_recurring_due = sum(due_schedules.mapped(lambda s: s.amount_recurring_taxinc - s.total_paid))
            t_amount_total_payment = sum(subscription.subscription_schedule.mapped('total_paid'))

            res['t_term_number'] = res['t_term_number'] + subscription.term_number
            res['t_amount_recurring_due'] = res['t_amount_recurring_due'] + t_amount_recurring_due
            res['t_amount_total_payment'] = res['t_amount_total_payment'] + t_amount_total_payment
            res['t_amount_total'] = res['t_amount_total'] + subscription.amount_total
            res['t_amount_recurring_taxinc'] = res['t_amount_recurring_taxinc'] + subscription.amount_recurring_taxinc
            res['t_amount_no_recurring_taxinc'] = res['t_amount_no_recurring_taxinc'] + subscription.amount_no_recurring_taxinc
            
            if subscription.subscription_schedule:                
                for line in subscription.subscription_schedule:
                    if line.payment_state not in ('paid','cancel'):
                        res['t_adeuda'] = True
                        break
                    
        return res
