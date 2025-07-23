# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class PracticeTypeFormCompletionQuestionnaire(models.Model):
    _name = 'practice.type.form.completion.questionnaire'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'PracticeTypeFormCompletionQuestionnaire'
    _rec_name = 'name_tutor'

    name_student = fields.Char('Name of Student') #*
    modality = fields.Char('Modality')#*
    campus = fields.Char('Campus') #sólo aplica si la modalidad es presencial o athome / LISTO EN LA VISTA
    area = fields.Char('area') #*
    #uno de estos puede no tener valores   / LISTO EN LA VISTA
    master_psychology_face_to_face = fields.Char('Master Psychology Face to Face')
    master_psychology_at_home = fields.Char('Master Psychology At Home')
    master_psychology_online = fields.Char('Master Psychology Online')
    master_neuroscience_face_to_face = fields.Char('Master neuroscience Face to Face')
    master_neuroscience_at_home = fields.Char('Mater Neuroscience At Home')
    master_neuroscience_online = fields.Char('Master Neuroscience Online')
    master_education_face_to_face = fields.Char('Master Education Face to Face')
    master_education_online = fields.Char('Master Education Online')
    master_education_at_home = fields.Char('Master Education At Home')
    master_speech_therapy_face_to_face = fields.Char('Master Speech Therapy Face to Face')
    master_speech_therapy_online = fields.Char('Master Speech Therapy Online')
    master_speech_therapy_at_home = fields.Char('Master Speech At Home')
    #solo tiene valores en algunos casos
    specialty_clinical_psychology = fields.Char('Specialty Psychology')
    specialty_psychology_child_youth = fields.Char('Child Youth')
    specialty_psychology_third_generation = fields.Char('Third Generation')
    #siempre tiene valores
    assessment_1 = fields.Integer('Presentación del Servicio de Prácticas (Información, documentación)')
    assessment_2 = fields.Integer('Coordinación de las prácticas por parte de ISEP')
    assessment_3 = fields.Integer('Apoyo durante el proceso de prácticas por parte de ISEP')
    #puede no tener valores (sólo se presenta cuando es online)
    typology_practices = fields.Char('Typology of Practices')
    #sólo se presenta cuando la tipología es  'Seguimiento de un caso (online)'
    assessment_4 = fields.Integer('Entorno Virtual')
    assessment_5 = fields.Integer('Información: presentación, metodología, calendario y guía para elaborar el informe')
    assessment_6 = fields.Integer('Materiales (videos, preguntas de reflexión y otros complementos')
    assessment_7 = fields.Integer('Herramientas de comunicación: foros y sesiones clinicas online')
    assessment_8 = fields.Integer('Tutor (dinamización, rapidez y calidad en la respuesta,...)')
    #puede no tener valores (sólo tiene valores cuando es online y además la tipología es 'Centro Externo')
    name_center_practice = fields.Char('Centro de Prácticas')
    name_tutor = fields.Char('Name Tutor')
    performed_hours = fields.Integer('Número de horas realizadas')

    #no tiene valores cuando la tipología es 'Seguimiento de un caso (online)'
    assessment_9 = fields.Char('Centro: instalaciones, ubicación física, servicios…')
    assessment_10 = fields.Char('Tutor de prácticas: trato, apoyo, seguimiento…')
    assessment_11 = fields.Char('Tareas realizadas')
    assessment_12 = fields.Char('Aportación personal del alumno a las actividades del centro.')
    #assessment_13 = fields.Integer('Relación de la experiencia con el contenido formativo del programa')

    #siempre tiene valores
    observations = fields.Text('Observations')
    number_hours_practice = fields.Integer('Number Hours Practice')
    assessment_14 = fields.Integer('Relación de las prácticas con el contenido formativo')
    assessment_15 = fields.Integer('Oportunidad de ampliar conocimientos en las prácticas')
    assessment_16 = fields.Integer('Experiencia válida para encontrar trabajo')
    assessment_17 = fields.Integer('Cumplimiento de expectativas')
    assessment_18 = fields.Integer('Valoración global de las prácticas')
    observations_suggestions = fields.Integer('Suggestions Observations')
    terms = fields.Char('Condiciones')
    #field PARA MOSTRAR LAS MAESTRÍAS
    # status_master = fields.Selection([
    #     ('master_psychology_face_to_face', 'Master Psicología Presencial'),
    #     ('master_psychology_at_home', 'Master Psicología At Home'),
    #     ('master_psychology_online', 'Master Psicología Online'),
    #     ('master_neuroscience_face_to_face', 'Master Neurosciencia Presencial'),
    #     ('master_neuroscience_at_home', 'Master Neurosciencia At Home'),
    #     ('master_neuroscience_online', 'Master Neuroscience Online'),
    #     ('master_education_face_to_face', 'Master Education Presencial'),
    #     ('master_education_online', 'Master Educación Online'),
    #     ('master_education_at_home', 'Master Educación At Home'),
    #     ('master_speech_therapy_face_to_face', 'Master Logopedia Presencial'),
    #     ('master_speech_therapy_online', 'Master Logopedia Online'),
    #     ('master_speech_therapy_at_home', 'Master Logopedia At Home'), ], 'Course',
    #     track_visibility='onchange', compute='_status_master')
    # status_specialty = fields.Selection([
    #     ('specialty_clinical_psychology', 'Especialidad Psicología Clinica'),
    #     ('specialty_psychology_child_youth', 'Especialidad Infantojuvenil'),
    #     ('specialty_psychology_third_generation', 'Especialidad Tercera Generación'), ], 'Specialty',
    #     track_visibility='onchange', compute='_status_specialty')



    # @api.depends('master_psychology_face_to_face', 'master_psychology_at_home', 'master_psychology_online',
    #              'master_neuroscience_face_to_face', 'master_neuroscience_at_home', 'master_neuroscience_online',
    #              'master_education_face_to_face', 'master_education_online', 'master_education_at_home',
    #              'master_speech_therapy_face_to_face', 'master_speech_therapy_online', 'master_speech_therapy_at_home')
    # def _status_master(self):
    #     if self.master_psychology_face_to_face:
    #         self.status_master = 'master_psychology_face_to_face'
    #     elif self.master_psychology_at_home:
    #         self.status_master = 'master_psychology_at_home'
    #     elif self.master_psychology_online:
    #         self.status_master = 'master_psychology_online'
    #     elif self.master_neuroscience_face_to_face:
    #         self.status_master = 'master_neuroscience_face_to_face'
    #     elif self.master_neuroscience_at_home:
    #         self.status_master = 'master_neuroscience_at_home'
    #     elif self.master_neuroscience_online:
    #         self.status_master = 'master_neuroscience_online'
    #     elif self.master_education_face_to_face:
    #         self.status_master = 'master_education_face_to_face'
    #     elif self.master_education_online:
    #         self.status_master = 'master_education_online'
    #     elif self.master_education_at_home:
    #         self.status_master = 'master_education_at_home'
    #     elif self.master_speech_therapy_face_to_face:
    #         self.status_master = 'master_speech_therapy_face_to_face'
    #     elif self.master_speech_therapy_online:
    #         self.status_master = 'master_speech_therapy_online'
    #     elif self.master_speech_therapy_at_home:
    #         self.status_master = 'master_speech_therapy_at_home'



    # @api.depends('specialty_clinical_psychology', 'specialty_psychology_child_youth',
    #              'specialty_psychology_third_generation')
    # def _status_specialty(self):
    #     if self.specialty_clinical_psychology:
    #         self.status_master = 'specialty_clinical_psychology'
    #     elif self.specialty_psychology_child_youth:
    #         self.status_master = 'specialty_psychology_child_youth'
    #     elif self.specialty_psychology_third_generation:
    #         self.status_master = 'specialty_psychology_third_generation'
