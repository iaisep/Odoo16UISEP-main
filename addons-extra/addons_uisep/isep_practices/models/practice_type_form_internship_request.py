# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class PracticeTypeFormInternshipRequest(models.Model):
    _name = 'practice.type.form.internship.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'PracticeTypeFormInternshipRequest'
    _rec_name = 'name_student'

    
    name_student = fields.Char('Name Student')
    specialty = fields.Char('Specialty', compute='compute_specialty')#A veces tiene valores, dependerá si no es vacío
    master = fields.Char('Master')
    campus = fields.Char('Campus')
    modality_enrollment = fields.Char('Modality Enrollment')
    #el que va en la vista
    option_practice = fields.Char('Option Practice', compute='compute_option_practice')
    turn = fields.Char('Turn')
    days = fields.Char('Days')
    #solo tiene valores cuando la opcion de prácticas es
    name_center = fields.Char('Name Center')
    name_contact_center = fields.Char('Name Contact Center')
    email_center = fields.Char('Email Center')
    province = fields.Char('Province')
    city = fields.Char('City')
    postal_code = fields.Char('Code Postal')
    #solo tiene valores cuando no es No aplica
    studying_year = fields.Char('Cursando Año')
    age_range = fields.Char('Age Range')
    #
    specialty_clinical_psychology = fields.Char('Specialty Psychology')
    specialty_psychology_child_youth = fields.Char('Specialty Child Youth')
    specialty_psychology_third_generation = fields.Char('Specialty Third Generation')
    specialty_art = fields.Char('Specialty Art')
    specialty_education = fields.Char('Specialty Education')
    #
    option_practice_1 = fields.Char()
    option_practice_2 = fields.Char()
    option_practice_3 = fields.Char()
    option_practice_4 = fields.Char()
    option_practice_5 = fields.Char()
    option_practice_6 = fields.Char()
    option_practice_7 = fields.Char()
    option_practice_8 = fields.Char()
    option_practice_9 = fields.Char()
    #Bool
    specialty_bool = fields.Boolean(compute='compute_specialty')
    studying_year_bool = fields.Boolean(compute='compute_studying_year')
    age_range_bool = fields.Boolean(compute='compute_age_range')


    def compute_specialty(self):
        self.specialty_bool = True
        if self.specialty_clinical_psychology:
            self.specialty = self.specialty_clinical_psychology
        elif self.specialty_psychology_child_youth:
            self.specialty = self.specialty_psychology_child_youth
        elif self.specialty_psychology_third_generation:
            self.specialty = self.specialty_psychology_third_generation
        elif self.specialty_art:
            self.specialty = self.specialty_art
        elif self.specialty_education:
            self.specialty = self.specialty_education
        else:
            self.specialty_bool = False


    def compute_option_practice(self):
        if self.option_practice_1:
            self.option_practice = self.option_practice_1
        elif self.option_practice_2:
            self.option_practice = self.option_practice_2
        elif self.option_practice_3:
            self.option_practice = self.option_practice_3
        elif self.option_practice_4:
            self.option_practice = self.option_practice_4
        elif self.option_practice_5:
            self.option_practice = self.option_practice_5
        elif self.option_practice_6:
            self.option_practice = self.option_practice_6
        elif self.option_practice_7:
            self.option_practice = self.option_practice_7
        elif self.option_practice_8:
            self.option_practice = self.option_practice_8

    
    @api.depends('studying_year')
    def compute_studying_year(self):
        self.studying_year_bool = True
        if self.studying_year == 'No aplica' or not self.studying_year_bool:
            self.studying_year_bool = False

    
    @api.depends('age_range')
    def compute_age_range(self):
        self.age_range_bool = True
        if self.age_range == 'No aplica' or not self.age_range:
            self.age_range_bool = False
