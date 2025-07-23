# -*- coding: utf-8 -*-
import logging
from datetime import datetime, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'


    link_card = fields.Char('link de registro de tarjeta', compute="compute_link_card")


    def send_link_card_for_mes_cron(self):
        date_start_tarjet = self.env['ir.config_parameter'].sudo().get_param('date_start_tarjet')
        # date_end_tarjet = self.env['ir.config_parameter'].sudo().get_param('date_end_tarjet')

        today = datetime.now().strftime('%Y-%m-%d')

        limit = 100  # Número de registros por lote
        offset = 0   # Desplazamiento inicial
                    
        total_records = self.env['sale.order'].search_count([
            ('stage_id.sequence', 'in', ['1', '2', '4']),
            ('payment_token_id', '=', False), 
            ('create_date', '>=', date_start_tarjet),
            ('create_date', '<=', today + ' 23:59:59')])
        

        while offset < total_records:
            records = self.env['sale.order'].search([
                ('stage_id.sequence', 'in', ['1', '2', '4']),
                ('payment_token_id', '=', False), 
                ('create_date', '>=', date_start_tarjet),
                ('create_date', '<=', today + ' 23:59:59')
            ], limit=limit, offset=offset)

            for record in records:
                record.create_link_card()
                self.send_mail_card_cron_mes(record)
            offset += limit  # Incrementa el desplazamiento para el siguiente lote


    def create_link_card(self):
        res_card_env = self.env['res.card']
        for o in self:
            res_card_env.create({
                'partner':o.partner_id.name,
                'partner_id': o.partner_id.id,
                'sale_id':o.id
            })
        


    def compute_link_card(self):
        res_card_env = self.env['res.card']
        for o in self:
            obj_card_env = res_card_env.sudo().search([
                ('partner_id','=',o.partner_id.id),
                ('active', '=', False),
                ('sale_id', '=', o.id) 
                ], order='create_date desc', limit=1)
            base_url = o.get_base_url()
            if obj_card_env:
                o.link_card = ('/').join((base_url,"card", obj_card_env.access_token))
            else:
                o.link_card = ""

    
    def send_mail_card_cron_mes(self, order):
        template_id = self.env.ref('isep_form_card_link.link_sign_card_template_sale_order').id
        template = self.env['mail.template'].sudo().browse(template_id)

        email_values = template.generate_email(order.id, ['body_html', 'subject', 'email_to', 'email_from'])
        email_body = email_values.get('body_html')
        subject = email_values.get('subject')
        email_to = email_values.get('email_to')
        email_from = email_values.get('email_from')

        template.sudo().send_mail(order.id, force_send=True)

        order.message_post(
            body=email_body,
            subject=subject,
            message_type='comment',
            subtype_id=self.env.ref('mail.mt_note').id,
            email_from=email_from,
            email_to=email_to
        )




