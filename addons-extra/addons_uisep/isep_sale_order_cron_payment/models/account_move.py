# -*- coding: utf-8 -*-
import logging
# from odoo.addons.payment import utils as payment_utils
from werkzeug import urls
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import hmac as hmac_tool
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    LIST_STATE = [
        ('is_sent', 'Link Pago Enviado'),
        ('not_send', 'Link Pago NO Enviado'),
    ]


    link_payment = fields.Char('Link de pago', compute = 'compute_link_payment_link')
    is_sent_mail = fields.Selection(LIST_STATE, string='Link de pago', default='not_send', copy=False,
                            tracking=True, help='Estado del link de pago')
    link_payment_static = fields.Char('Link de pago estático')



    def compute_link_payment_link(self):
        provider_id = self.env['payment.provider'].search([('use_payment_automatic','=',True)], limit=1)
        for payment_link in self:
            related_document = payment_link
            base_url = related_document.get_base_url()
            acces_toke = related_document._get_access_token()
            url_params = {
                'reference': payment_link.payment_reference,
                'amount': payment_link.amount_residual,
                'access_token': acces_toke,
            }
            payment_link.link_payment = f'{base_url}/payment/pay?{urls.url_encode(url_params)}&invoice_id={payment_link.id}&provider_id={provider_id.id}' or ''


    def cron_generate_payment_links(self):
        today = fields.Date.today()
        three_months_ahead = today + timedelta(days=90)
        invoices = self.search([
            ('invoice_date', '>=', today),
            ('invoice_date', '<=', three_months_ahead),
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            '|',
            ('link_payment_static', '=', False),
            ('link_payment_static', '=', ''),
        ])
        for invoice in invoices:
            invoice.compute_link_payment_link()
            invoice.link_payment_static = invoice.link_payment


    # def _get_access_token(self):
    #     self.ensure_one()
    #     return payment_utils.generate_access_token(
    #         self.partner_id.id, 
    #         self.amount_residual,
    #         self.currency_id.id
    #     )    

    def _get_access_token(self):
        self.ensure_one()
        try:
            if not self.partner_id or not self.amount_residual or not self.currency_id:
                _logger.error("Datos insuficientes para generar el token de acceso para el registro %s", self.id)
                return ''

            # Generar el token de acceso sin usar `request`
            token_str = '|'.join(str(val) for val in [
                self.partner_id.id,
                self.amount_residual,
                self.currency_id.id
            ])
            access_token = hmac_tool(self.env(su=True), 'generate_access_token', token_str)
            return access_token
        except Exception as e:
            _logger.error("Error al generar el token de acceso para el registro %s: %s", self.id, str(e))
            return ''


    
    def send_template_link_payment(self):
        template_id = self.env.ref('isep_sale_order_cron_payment.link_card_email_template_invoice').id
        template = self.env['mail.template'].sudo().browse(template_id)

        invoices = self.browse(self._context.get('active_ids'))
        for invoice in invoices:
            if invoice.is_sent_mail == 'not_send' and invoice.state == 'posted' and invoice.move_type == 'out_invoice':

                email_values = template.generate_email(invoice.id, ['body_html', 'subject', 'email_to', 'email_from'])
                email_body = email_values.get('body_html')
                subject = email_values.get('subject')
                email_to = email_values.get('email_to')
                email_from = email_values.get('email_from')

                template.sudo().send_mail(invoice.id, force_send=True)

                invoice.message_post(
                    body=email_body,
                    subject=subject,
                    message_type='email',
                    subtype_id=self.env.ref('mail.mt_comment').id,
                    email_from=email_from,
                    email_to=email_to
                )

                invoice.is_sent_mail = 'is_sent'
                invoice.link_payment_static = invoice.link_payment


    def send_template_link_payment_massive(self):
        today = fields.Date.today()
        # Convertir la fecha de hoy a datetime
        today_start = datetime.combine(today, datetime.min.time())
        today_end = today_start + timedelta(days=1)
        # account_move_record = self.search([('create_date','<=', today)])
        account_move_record = self.search([('create_date', '>=', today_start), ('create_date', '<', today_end)])

                
        template_id = self.env.ref('isep_sale_order_cron_payment.link_card_email_template_invoice').id
        template = self.env['mail.template'].sudo().browse(template_id)

        for invoice in account_move_record:

            if invoice.is_sent_mail == 'not_send' and invoice.state == 'posted' and invoice.move_type == 'out_invoice':

                email_values = template.generate_email(invoice.id, ['body_html', 'subject', 'email_to', 'email_from'])
                email_body = email_values.get('body_html')
                subject = email_values.get('subject')
                email_to = email_values.get('email_to')
                email_from = email_values.get('email_from')

                template.sudo().send_mail(invoice.id, force_send=True)

                invoice.message_post(
                    body=email_body,
                    subject=subject,
                    message_type='email',
                    subtype_id=self.env.ref('mail.mt_comment').id,
                    email_from=email_from,
                    email_to=email_to
                )

                invoice.is_sent_mail = 'is_sent'
                invoice.link_payment_static = invoice.link_payment
