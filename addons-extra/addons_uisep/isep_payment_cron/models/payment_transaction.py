from odoo import api, fields, models, Command
from odoo.exceptions import UserError
from datetime import date, timedelta, datetime
from collections import defaultdict 
import psycopg2
import requests
import logging
_logger = logging.getLogger(__name__)

class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'
    
    custom_cron = fields.Boolean(string="Cron personalizado", default=False )
    one_payment_done = fields.Boolean(string="Pago asociado", default=False)

    #date_fake= fields.Datetime(string="Fecha fake")

    def write(self, vals):
        for record in self:
            current_state = record.state
            custom_cron = record.custom_cron    
            one_payment_done = record.one_payment_done        
            result = super(PaymentTransaction, self).write(vals)            
            if 'state' in vals and vals['state'] == 'done' and current_state != 'done' and one_payment_done == False and custom_cron == True:
                record.one_payment_done = True
                try:                    
                    record._finalize_post_processing()
                    self.env.cr.commit()
                except Exception as e:
                    _logger.error(
                        f"Error durante el post-procesamiento de la transacción {record.id}: {str(e)}"
                    )        
            return result
    
    def _get_payment_token_order(self, invoice):
        source_orders = invoice.line_ids.sale_line_ids.order_id
        order_id = False
        for order in source_orders:
            order_id = order
            break
        if not order_id or not order_id.payment_token_id:
            msn_error = "No se encontró un método de pago tokenizado para el cliente"
            raise UserError(msn_error)
        return order_id
    
    def _send_build_payment_request(self,invoice, order, payment_token, pendiente):
        if not pendiente or pendiente > 100:
            return
        factor = pendiente*0.01
        current_time = datetime.now()
        time_cron = current_time.strftime("%H:%M:%S.%f")[:-2] # ("%d/%m/%y %H:%M:%S.%f")[:-3]
        COP = self.env.ref('base.COP').id
        amount_residual = invoice.amount_residual
        if pendiente != 100:
            amount_residual = round(amount_residual*factor,2)
        if invoice.currency_id.id == COP and amount_residual > 999999:
            amount_residual = 999999

        try:            
            transaction = self.env['payment.transaction'].create({
                'amount': amount_residual,
                'currency_id': invoice.currency_id.id,
                'partner_id': invoice.partner_id.id,
                'token_id': payment_token.id,
                'invoice_ids': [(6, 0, [invoice.id])], 
                'provider_id': payment_token.provider_id.id,
                'operation': 'online_token',
                'reference': '%s:%s-%s' % (order.name,invoice.name,time_cron),
                #'callback_model_id': self.env['ir.model'].sudo()._get_id(order._name),
                #'callback_res_id': order.id,
                'callback_method': 'reconcile_pending_transaction',
                'custom_cron':True,
            })
            self.env.cr.commit()
                
            transaction._send_payment_request()  # Método para enviar la solicitud de pago            
            self.env.cr.commit()


        except Exception as e:
            self.env.cr.rollback()  # Revertir en caso de errores
            _logger.error(f"Error al procesar el pago para la factura con ID {invoice.id}: {str(e)}")
        



    def _cron_recurring_payment_sale_order(self, meses=None, previsualizar=False, pendiente=False , conpany_all=False):
        if not pendiente or pendiente > 100:
            return
        sale_order = self.env['sale.order']
        today = date.today()
        # Dominio para encontrar las órdenes de venta pendientes de pago
        domain = [
            ('state', 'in', ('sale', 'done')),  # Órdenes confirmadas
            ('stage_id.custom_cron', '=', True),  # etapa marcada para cobrar
            ('payment_token_id', '!=', False),  # Suscripciones con token
        ]
        sale_orders = sale_order.search(domain)

        if not sale_orders:
            _logger.info("No se encontraron órdenes pendientes de pago para procesar.")
            return "No se encontraron órdenes pendientes de pago para procesar."

        deadline = None
        if meses and isinstance(meses, int) and meses > 0:
            deadline = today - timedelta(days=meses * 30)  # Aproximación: 30 días por mes

        invoices_to_process = [] 

        for sale in sale_orders:
            payment_token = sale.payment_token_id
            company_token = sale.payment_token_id.company_id
            order_invoice_ids = False
            
            if conpany_all:
                order_invoice_ids = sale.invoice_ids.filtered(
                        lambda inv: inv.state == 'posted' and
                                    inv.payment_state in ('not_paid', 'partial') and
                                    inv.move_type == 'out_invoice'                                    
                    )
            else:
                order_invoice_ids = sale.invoice_ids.filtered(
                        lambda inv: inv.state == 'posted' and
                                    inv.payment_state in ('not_paid', 'partial') and
                                    inv.move_type == 'out_invoice' and
                                    inv.company_id.id == company_token.id
                    )                   

            for invoice in order_invoice_ids:
                # Saltar facturas fuera del rango de meses, si corresponde
                if deadline and invoice.invoice_date_due < deadline:
                    continue

                # Controlar facturas con fecha futura
                if invoice.invoice_date_due > today:
                    continue

                if previsualizar:
                    COP = self.env.ref('base.COP').id
                    factor = pendiente*0.01
                    amount_residual = invoice.amount_residual
                    if pendiente != 100:
                        amount_residual = round(amount_residual*factor,2)
                    if invoice.currency_id.id == COP and amount_residual > 999999:
                        amount_residual = 999999
                    invoices_to_process.append({
                        'id': invoice.id,
                        'invoice': invoice.name,
                        'date': invoice.invoice_date,
                        'date_due': invoice.invoice_date_due,
                        'partner': invoice.partner_id.name or 'REVISAR',
                        'amount_residual': amount_residual,
                        'currency': invoice.currency_id.name or 'REVISAR',
                    })
                else:
                    # Procesar factura normalmente
                    try:
                        self._send_build_payment_request(invoice, sale, payment_token,pendiente)
                        _logger.info(f"Pago procesado para la factura {invoice.name}.")
                    except Exception as e:
                        _logger.error(f"Error procesando la factura {invoice.name}: {e}")
    
        if previsualizar:
            if invoices_to_process:
                result = "\n".join([
                    f"ID: {item['id']}, Factura: {item['invoice']}, Fecha: {item['date']}, Fecha vencimiento: {item['date_due']}, Cliente: {item['partner']}, Pendiente de pago: {item['amount_residual']}, Moneda: {item['currency']}"
                    for item in invoices_to_process
                ])
                raise UserError(f"Facturas a procesar:\n{result}")
            else:
                raise UserError("No hay facturas válidas para procesar.")


        return "Tarea de cron completada."


    def _force_recurring_payment_invoice(self, inv,pendiente):
        if inv.state == 'posted' and inv.payment_state in ('not_paid', 'partial') and inv.move_type == 'out_invoice':            
            order_id = self._get_payment_token_order(inv)            
            self._send_build_payment_request(inv, order_id, order_id.payment_token_id,pendiente)
        return "Intento de cobro de factura completada."

    @api.model
    def check_repeated_payment_errors(self, webhook=False):
        link_pay = ''
        today = fields.Date.today()
        first_day = today.replace(day=1)
        last_day = (first_day + timedelta(days=32)).replace(day=1) - timedelta(days=1)

        transactions = self.search([
            ('state', '=', 'error'),
            ('create_date', '>=', first_day),
            ('create_date', '<=', last_day),
            ('sale_order_ids', '!=', False),
        ])

        sale_order_error_count = defaultdict(int)
        for tx in transactions:
            for order in tx.sale_order_ids:
                sale_order_error_count[order.id] += 1


        problematic_orders = [
            order_id for order_id, count in sale_order_error_count.items()
            if count >= 3
        ]
        
        if problematic_orders:
            search_domain = [('id', 'in', problematic_orders)]
            sale_orders = self.env['sale.order'].search(search_domain,limit=1)
            
            if sale_orders.card == True:
                res_card_env = self.env['res.card']
                res_card = res_card_env.create({
                    'partner': sale_orders.partner_id.name,
                    'partner_id': sale_orders.partner_id.id,
                })

                wizard = self.env['isep.form.data.wizard'].with_context(
                    get_sale_order_id=sale_orders.id,
                    get_token=res_card.access_token
                ).create({'sale_order_id': sale_orders.id})
                link_pay = wizard.order_start_url

            else:
                res_card_env = self.env['res.card']
                res_card = res_card_env.create({
                    'partner': sale_orders.partner_id.name,
                    'partner_id': sale_orders.partner_id.id,
                })

                wizard = self.env['isep.form.data.wizard'].with_context(
                    get_sale_order_id=sale_orders.id,
                    get_token=res_card.access_token
                ).create({'sale_order_id': sale_orders.id})
                sale_orders.write({
                    'card': True,
                })
                link_pay = wizard.order_start_url

            transaction = self.search([
                ('state', '=', 'error'),
                ('sale_order_ids', 'in', sale_orders.id)
            ], limit=1)

            if transaction and transaction.partner_id.email:
                template = self.env.ref('isep_payment_cron.email_template_transacction')
                template.with_context(
                    email_to=transaction.partner_id.email,
                    email_from=self.env.user.partner_id.email,
                    send_email=True,
                    link_pay=link_pay,
                    attendee=transaction.partner_id.name,
                ).send_mail(transaction.id, force_send=True, raise_exception=False)
            
            
            if webhook:
                data = {
                    "name": transaction.partner_id.name,
                    "email": transaction.partner_id.email,
                    "telefono": transaction.partner_id.phone,
                    "movil": transaction.partner_id.mobile,
                    "link_pay": link_pay,
                }
                try:
                    response = requests.post(webhook, json=data, timeout=10)
                    response.raise_for_status()  
                except Exception as e:
                    _logger = self.env['ir.logging']._get_logger()
                    _logger.warning(f"Webhook error: {str(e)}")

            # sale_orderss = self.env['sale.order'].browse(problematic_orders)
            # order_names = ', '.join(sale_orderss.mapped('name'))
            # raise UserError(f"Las siguientes órdenes tienen 3 o más transacciones con error este mes: {order_names}")
