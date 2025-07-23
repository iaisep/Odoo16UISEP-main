# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class PracticeTypeFormCenter(models.Model):
    _name = 'practice.type.form.center'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'PracticeTypeFormCenter'

    name = fields.Char('Name of Center')
    coordinator = fields.Char('Name of Coordinator')
    official_name = fields.Char('Official Name')
    signatory_name = fields.Char('Signatory Name')
    postal_code = fields.Char('Postal Code')
    province = fields.Char('Province')
    city = fields.Char('City')
    street = fields.Char('Street')
    number_places = fields.Char('Number Places')
    phone = fields.Char('Phone')
    mobil = fields.Char('Mobil')
    email = fields.Char('Email')
    website = fields.Char('Website')
    turn = fields.Char('Turn')
    days = fields.Char('Days')
    status_form_center = fields.Selection([
        ('not generated', 'No Generado'),
        ('generated', 'Generado'),
        ('problems to be generated', 'Problemas Para Ser Generado'), ], 'Status Form Center', track_visibility='onchange')
    update = fields.Boolean('Location Update')
    # update_zip = fields.Many2one('res.better.zip', string='Localitation')
    # update_city = fields.Char('City Update', related='update_zip.city', store=True)
    # update_province = fields.Many2one('res.country.state', string='Province Update', related='update_zip.state_id',
    #                                   store=True)
    # update_country = fields.Many2one('res.country', string='Country Update', related='update_zip.country_id',
    #                                  store=True)
    # update_code = fields.Char(string='Postal Code', related='update_zip.name', store=True)
    day_order = fields.Char('ORDER', compute='computeTurn')
    create_schedule = fields.Boolean('Create Schedule')
    practice_schedule_id = fields.Many2one('practice.schedule', string="Register Schedule")

    
    @api.depends('days', 'turn')
    def computeTurn(self):
        if isinstance(self.days, list):  # Check if self.days is a list
            # Join days into a single string and clean up brackets and quotes
            joins = ''.join(self.days)
            replace1 = joins.replace('[', '')
            replace2 = replace1.replace(']', '')
            replace3 = replace2.replace(",", '')
            replace_total = replace3.replace("'", '')
            
            # Split cleaned string into individual day elements
            _days = replace_total.split()
            
            # Define the order of days for sorting
            order = {'Lunes': 0, 'Martes': 1, 'Miercoles': 2, 'Jueves': 3, 'Viernes': 4, 'Sabado': 5}
            
            # Create a list of tuples with each day and its order value
            order_day = []
            for d in _days:
                valor = order.get(d)
                if valor is not None:  # Ensure day is in the order dictionary
                    order_day.append((valor, d))
            
            # Sort the days based on order
            order_day.sort()
            
            # Extract sorted day names and join them with commas
            total_day = [day for _, day in order_day]
            mzcl = ', '.join(total_day)
            
            # Set the computed value for day_order
            self.day_order = f"{mzcl} - {self.turn}"
        else:
            self.day_order = f"Invalid days format - {self.turn}"

        # joins = ''.join(self.days)
        # replace1 = joins.replace('[','')
        # replace2 = replace1.replace(']','')
        # replace3 = replace2.replace(",", '')
        # replace_total = replace3.replace("'",'')
        # _days = replace_total.split()
        # order = {'Lunes':0,'Martes':1,'Miercoles':2,'Jueves':3, 'Viernes':4, 'Sabado':5}
        # order_day = []
        # for d in _days:
        #     valor = order[d]
        #     order_day.append((valor, d))
        # order_day.sort()
        # or_d = dict(order_day)
        # total_day = [day for day in or_d.values()]
        # mzcl = ', '.join(total_day)
        # self.day_order = mzcl+' - '+self.turn


    def addTurnDay(self):
        schedule = self.env['practice.schedule'].search([('name', '=', self.day_order)])
        if len(schedule) > 0:
            return schedule.id
        if self.create_schedule and self.practice_schedule_id:
            if self.day_order == self.practice_schedule_id.name:
                return self.practice_schedule_id.id
            return -1
        return 0


    def generateCenter(self):
        pass
        # country = self.env['res.country'].search([('code', '=', 'ES')])
        # country_state = self.env['res.country.state'].search([('name', '=', self.province),
        #                                                       ('country_id', '=', country.id)])
        # zip = self.env['res.better.zip'].search([('name', '=', self.postal_code), ('city', '=', self.city),
        #                                          ('state_id', '=', country_state.id),
        #                                          ('country_id', '=', country.id)])

        # if len(zip) > 0 and self.status_form_center != 'generated':
        #     value = {
        #         'center': True,
        #         'name': self.name,
        #         'country_id': zip.country_id.id,
        #         'state_id': zip.state_id.id,
        #         'zip_id': zip.id,
        #         'zip': zip.name,
        #         'city': zip.city,
        #         'name_official': self.official_name,
        #         'street': self.street,
        #         'maximum_places': self.number_places,
        #         'mobile': self.mobil,
        #         'phone': self.phone,
        #         'email': self.email,
        #         'coordinator': self.coordinator,
        #         'website': self.website,
        #         'signatory': self.signatory_name
        #     }
        #     typeform_center = self.search([('id', '=', self.id)])
        #     typeform_center.write({'status_form_center': 'generated'})
        #     self.env["res.partner"].create(value)
        # elif self.update and self.update_zip and self.addTurnDay() > 0:
        #     value = {
        #         'center': True,
        #         'name': self.name,
        #         'country_id': self.update_country.id,
        #         'state_id': self.update_province.id,
        #         'zip_id': self.update_zip.id,
        #         'zip': self.update_code,
        #         'city': self.update_city,
        #         'name_official': self.official_name,
        #         'street': self.street,
        #         'maximum_places': self.number_places,
        #         'mobile': self.mobil,
        #         'phone': self.phone,
        #         'email': self.email,
        #         'coordinator': self.coordinator,
        #         'signatory': self.signatory_name,
        #         'website': self.website,
        #         'status_form_center': 'generated',
        #         'practice_schedule_id': self.addTurnDay()
        #     }
        #     typeform_center = self.search([('id', '=', self.id)])
        #     typeform_center.write({'status_form_center': 'generated'})
        #     self.env["res.partner"].create(value)
        # elif self.addTurnDay() == 0:
        #     raise ValidationError(
        #         _("Debe crear el horario, porque no se tiene registrado"))
        # elif self.addTurnDay() == -1:
        #     raise ValidationError(
        #         _("El horario que creo no coincide con el orden del horario del centro"))
        # else:
        #     typeform_center = self.search([('id', '=', self.id)])
        #     typeform_center.write({'status_form_center': 'not generated'})
        #     raise ValidationError(
        #         _("Debes actualizar la ubicación porque los datos de ubicación son erroneos"))
