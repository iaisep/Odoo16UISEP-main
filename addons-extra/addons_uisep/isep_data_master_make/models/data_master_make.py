# -*- coding: utf-8 -*-
import re
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class DataMasterMake(models.Model):
    _name = 'data.master.make'
    _description = 'DataMasterMake'

    name_student = fields.Char('Nombre del Estudiante')
    name_admission = fields.Char('Nombre de la admisión')
    date_first_payment = fields.Date('Fecha del primer pago')
    date_start_class = fields.Date('Fecha de inicio de clases')
    progress_campus = fields.Float('Porcentaje de avance en campus')
    name_suscription = fields.Char('Suscripción')
    email = fields.Char('Correo')
    phone = fields.Char('Teléfono')


    def action_send_data(self):
        data = self.env['data.master.make']
        admissions = self.env['op.admission'].search([('state', '=', 'done'), ('order_id', '!=', False)])

        if admissions:
            for admission in admissions:

                existing_record = data.search([
                    ('name_student', '=', admission.partner_id.name),
                    ('name_suscription', '=', admission.order_id.name)
                ])

                # clean_phone = re.sub(r'\D', '', admission.partner_id.phone)

                values = {
                    'name_student': admission.partner_id.name,  
                    'name_admission': admission.register_id.name,
                    'date_first_payment': admission.order_id.start_date,  
                    'date_start_class': admission.batch_id.date_start_class,  
                    # 'progress_campus': student.progress_campus,
                    'name_suscription': admission.order_id.name,
                    'phone': re.sub(r'\D', '', admission.partner_id.phone) if admission.partner_id.phone else '',
                    'email': admission.partner_id.email,
                }

                if existing_record:
                    existing_record.write(values)
                else:
                    data.create(values)
        



