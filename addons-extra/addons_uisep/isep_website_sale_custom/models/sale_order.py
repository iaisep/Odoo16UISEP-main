# -*- coding: utf-8 -*-
import logging
from datetime import datetime, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta
from datetime import date
_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    
    send_sign = fields.Boolean('Firma enviado', compute="_compute_send_sign")     
    website_send_mail = fields.Boolean('Correo enviado')
    is_from_website_origin = fields.Boolean('Venta desde ecommerce')
    
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        if self.recurrence_id and not self.subscription_schedule:
            self.create_subscription_schedule()
            
        order_line = self.order_line.filtered(lambda x: x.product_template_id.is_academic_program and x.product_template_id.recurring_invoice )
        if order_line and not self.website_send_mail and self.is_from_website_origin:
            self.send_automated_action()
            self.website_send_mail = True
            
        return res
    
    def get_partner_gender(self):
        gender_values = [('m', 'Masculino'), ('f', 'Femenino'), ('o', 'Otro')]
        return gender_values
        

    def get_admission_availability(self):
        today = date.today()
        admission_periods = []

        for i in range(3):  # Mes actual + 2 futuros
            future_date = (today.replace(day=1) + timedelta(days=31 * i)).replace(day=1)
            year = future_date.year
            month = future_date.month
            period = future_date.strftime('%Y-%m-%d')
            month_name = future_date.strftime('%B')

            meses = {
                'January': 'Enero', 'February': 'Febrero', 'March': 'Marzo',
                'April': 'Abril', 'May': 'Mayo', 'June': 'Junio',
                'July': 'Julio', 'August': 'Agosto', 'September': 'Septiembre',
                'October': 'Octubre', 'November': 'Noviembre', 'December': 'Diciembre'
            }
            label = f"{meses[month_name]} {year}"

            admission_periods.append((period, label))

        return admission_periods
        
    
    def _process_custom_form(self, partner_id, form_data):
        """
        Procesamos los datos recibidos del formulario.
        """
        if self.error_admission:
            raise UserError("Error en orden.")
        custom_data = form_data
        
        data_dict = {}
        for line in custom_data.split('\n'):
            if ' : ' in line:
                key, value = line.split(' : ', 1)
                data_dict[key.strip()] = value.strip()
                
        def parse_date(date_str):
            try:
                return datetime.strptime(date_str, "%d/%m/%Y").strftime("%Y-%m-%d")
            except ValueError:
                return False  # Aseguramos el valor

        birth_date = parse_date(data_dict.get('birth_date', ''))
        finalizacion_estudios = parse_date(data_dict.get('finalizacionestudios', ''))

        partner_vals = {
            'name': data_dict.get('partner_name', 'Sin Nombre'),
            'birth_date': birth_date if birth_date else None,
            'university': data_dict.get('university', ''),
            'gender': data_dict.get('gender', ''),
            'profession': data_dict.get('profession', ''),
            'titulacion': data_dict.get('titulacion', ''),
            'finalizacionestudios': finalizacion_estudios if finalizacion_estudios else None,
            'phone': data_dict.get('phone', ''),
        }
        self.admission_date = data_dict.get('admission_date', False)
        self.gender =  data_dict.get('gender', '')
        self.partner_id.gender = data_dict.get('gender', '')
        if not self.product_template_id or not self.course_id:
            self.get_academic_product_template_id()
            
        self.is_from_website_origin = True
        self._compute_period()
        
        
        partner_id.write(partner_vals)


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('website_id'):
                recurrence_record = self.env['sale.temporal.recurrence'].search([
                    ('use_public_auto', '=', True)
                    ], limit=1)
                vals['recurrence_id'] = recurrence_record.id
                vals['start_date'] = fields.Date.today()

        return super().create(vals_list)



    def send_automated_action(self):
        self.action_send_to_sign()
        if self.sign_id:
            self.sign_id.create_link_sign()
            self.send_mail_sign_website()

            


    
    def send_mail_sign_website(self):
        template_id = self.env.ref('isep_website_sale_custom.link_sign_website_template_sale_order').id
        # template = self.env['mail.template'].sudo().browse(template_id)

        self.with_context(force_send=True).message_post_with_template(template_id, email_layout_xmlid=False)
        
        """email_values = template.generate_email(order.id, ['body_html', 'subject', 'email_to', 'email_from'])
        email_body = email_values.get('body_html')
        subject = email_values.get('subject')
        email_to = email_values.get('email_to')
        email_from = email_values.get('email_from')

        template.sudo().send_mail(order.id, force_send=True)

        order.message_post(
            body=email_body,
            subject=subject,
            message_type='email',
            subtype_id=self.env.ref('mail.mt_comment').id,
            email_from=email_from,
            email_to=email_to
        )"""


    def _compute_send_sign(self):
        for o in self:
            if o.sign_id:
                o.send_sign = True
            else:
                o.send_sign = False
            
