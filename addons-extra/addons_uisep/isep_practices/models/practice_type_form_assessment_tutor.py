# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class PracticeTypeFormAssessmentTutor(models.Model):
    _name = 'practice.type.form.assessment.tutor'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'PracticeTypeFormAssessmentTutor'
    _rec_name = 'name_tutor'

    name_tutor = fields.Char('Name of Tutor')
    name_center = fields.Char('Name of Center')
    name_student = fields.Char('Name of Student')
    city = fields.Char('City')
    area = fields.Char('Area')
    master_psychology_bool = fields.Boolean(compute="_psychology_bool")
    master_neuropsychology_bool = fields.Boolean(compute="_neuropsychology_bool")
    master_study_bool = fields.Boolean(compute="_study_bool")
    master_speech_therapy_bool = fields.Boolean(compute="_speech_therapy_bool")
    master_psychology = fields.Char('Master')
    master_neuropsychology = fields.Char('Master')
    master_study = fields.Char('Master')
    master_speech_therapy = fields.Char('Master')
    assessment_responsibility = fields.Integer('Assessment in Responsibility')
    assessment_started = fields.Integer('Assessment Started')
    assessment_teacher_interaction = fields.Integer('Teacher Interaction')
    assessment_patients_interaction = fields.Integer('Patients Interaction')
    assessment_capacity_observation = fields.Integer('Observation Capacity')
    assessment_capacity_participation = fields.Integer('Capacity Participation')
    assessment_meets_set_objectives = fields.Integer('Meets Set Objectives')
    assessment_ability_to_take_cases = fields.Integer('ability to take cases')
    assessment_involvement_development_material = fields.Integer('Involvement in the Development of the Material')
    assessment_evaluation_internship_period_general = fields.Integer('Evaluation of the internship period in general')
    assessment_observations = fields.Html('Observations')


    @api.depends('master_psychology')
    def _psychology_bool(self):
        self.master_psychology_bool = True
        if not self.master_psychology:
            self.master_psychology_bool = False


    
    @api.depends('master_neuropsychology')
    def _neuropsychology_bool(self):
        self.master_neuropsychology_bool = True
        if not self.master_neuropsychology:
            self.master_neuropsychology_bool = False


    @api.depends('master_study')
    def _study_bool(self):
        self.master_study_bool = True
        if not self.master_study:
            self.master_study_bool = False


    @api.depends('master_speech_therapy')
    def _speech_therapy_bool(self):
        self.master_speech_therapy_bool = True
        if not self.master_speech_therapy:
            self.master_speech_therapy_bool = False

    
    def ratings_student(self):
        ratings = [self.assessment_responsibility, self.assessment_started,
                   self.assessment_teacher_interaction, self.assessment_patients_interaction,
                   self.assessment_capacity_observation, self.assessment_capacity_participation,
                   self.assessment_meets_set_objectives, self.assessment_ability_to_take_cases,
                   self.assessment_involvement_development_material,
                   self.assessment_evaluation_internship_period_general]
        ratings_sum = sum(ratings)
        rating_total = ratings_sum / len(ratings)
        print(rating_total)