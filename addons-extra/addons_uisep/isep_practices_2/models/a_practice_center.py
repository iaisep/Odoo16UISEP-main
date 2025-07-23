# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime


class PracticeCenter(models.Model):
    _name = 'practice.center'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Practice Center'

    name = fields.Char('Center Name', help="The name of the practice center.")
    coordinator = fields.Char('Coordinator Name', help="The name of the coordinator responsible for the center.")
    official_name = fields.Char('Official Name', help="The official name of the practice center.")
    signatory_name = fields.Char('Signatory Name',
                                 help="The name of the person authorized to sign documents for the center.")
    postal_code = fields.Char('Postal Code', help="The postal code where the practice center is located.")
    province = fields.Char('Province', help="The province where the practice center is located.")
    city = fields.Char('City', help="The city where the practice center is located.")
    street = fields.Char('Street', help="The street address of the practice center.")
    number_places = fields.Char('Number of Places', help="The number of available places in the practice center.")
    phone = fields.Char('Phone', help="The phone number of the practice center.")
    mobil = fields.Char('Mobile', help="The mobile number of the practice center.")
    email = fields.Char('Email', help="The email address of the practice center.")
    website = fields.Char('Website', help="The website of the practice center.")
    turn = fields.Char('Shift', help="The operating shift of the practice center (e.g., morning, afternoon).")
    days = fields.Char('Days', help="The operating days of the practice center (e.g., Monday-Friday).")
    status_form_center = fields.Selection([
        ('not generated', 'No Generado'),
        ('generated', 'Generado'),
        ('problems to be generated', 'Problemas al generar')],
        'Form Center Status',
        help="The current status of the form center.",
        tracking=True,
    )
    update = fields.Boolean('Location Update', help="Indicates if the location of the center has been updated.")
    create_schedule = fields.Boolean('Create Schedule',
                                     help="Indicates if a schedule needs to be created for the practice center.")
    schedule_description = fields.Text("Schedule Description",
                                       help="Indicates how schedule needs to be created for the practice center.")
    practice_schedule_id = fields.Many2one(
        'practice.schedule',
        string="Registered Schedule",
        help="The schedule registered for this practice center."
    )
    partner_id = fields.Many2one(
        'res.partner',
        string="Partner",
        help="The partner associated with this practice center."
    )
    country_id = fields.Many2one('res.country', string='Country', default=lambda self: self.env.company.country_id)
    state_id = fields.Many2one('res.country.state', string="State", domain="[('country_id', '=?', country_id)]")
    zip_id = fields.Many2one(
        "res.city.zip",
        string="ZIP Location",
        help="Use the city name or the zip code to search the location",
        domain="[('state_id', '=?', state_id)]"
    )

    tutor_ids = fields.One2many(
        comodel_name="res.partner",
        inverse_name="center_id",
        string="Tutors",
        domain=[('tutor', '=', True)],
        help="Tutors related to this practice center."
    )
    op_course_ids = fields.Many2many(
        comodel_name="op.course",
        inverse_name="center_id",
        string="Courses",
        help="Course related to this practice center."
    )

    schedule_ids = fields.One2many(
        'practice.center.schedule',
        'center_id',
        string="Practice Schedules"
    )
    type_ids = fields.Many2many(
        comodel_name="practice.center.type",
        inverse_name="center_id",
        string="Types of Practices",
        help="practice.center.type"
    )

    center_count = fields.Integer(string='Centers', compute='_center_count')

    @api.depends('name')  # Puedes poner otros campos dependientes si es necesario
    def _center_count(self):
        for record in self:
            # Cuenta los registros de práctica
            record.center_count = 1

    # Función para convertir hora en formato HH:MM:SS a decimal
    def time_to_decimal(self, time_str):
        time_obj = datetime.strptime(time_str, '%H:%M:%S')  # Convertir la cadena a objeto datetime
        return time_obj.hour + time_obj.minute / 60.0  # Convertir a formato decimal

    def create_schedule2(self):
        # Definir los valores predeterminados para el horario a crear
        schedule_vals = {
            'center_id': self.id,  # Relacionamos este horario con el centro de prácticas actual
            'shift_id': self.env.ref('isep_practices_2.shift_morning').id,  # Seleccionamos un turno predeterminado
            'day_of_week_id': self.env.ref('isep_practices_2.day_monday').id,  # Seleccionamos un día predeterminado
            'start_time': self.time_to_decimal('08:00:00'),  # Hora de inicio por defecto
            'end_time': self.time_to_decimal('12:00:00'),  # Hora de fin por defecto
            'description': 'Horario del turno de mañana',  # Descripción predeterminada
        }

        # Crear el nuevo horario
        self.env['practice.center.schedule'].create(schedule_vals)

        # Opcionalmente, mostrar un mensaje confirmando la creación
        self.message_post(body="Se ha creado un nuevo horario de prácticas.")

        return True


    @api.onchange('zip_id')
    def _onchange_zip_id(self):
        """
        Updates the city name based on the selected ZIP location.
        """
        if self.zip_id:
            self.city = self.zip_id.city_id.name
            self.province = self.state_id.name
            self.postal_code = self.zip_id.name
        else:
            self.city = False

    def create_res_partner(self):
        """Creates a corresponding res.partner record for the practice center."""
        for center in self:
            partner_vals = {
                'name': center.name,
                'phone': center.phone,
                'mobile': center.mobil,
                'email': center.email,
                'website': center.website,
                'street': center.street,
                'city': center.city,
                'zip': center.postal_code,
                'state_id': self.env['res.country.state'].search([('name', '=', center.province)], limit=1).id,
                'center': True
            }
            partner = self.env['res.partner'].create(partner_vals)
            center.partner_id = partner.id
            if center.partner_id:
                center.status_form_center = "generated"
            else:
                center.status_form_center = "not generated"

