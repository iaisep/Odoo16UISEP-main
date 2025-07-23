# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)
ratings = [
    ("NR", "NR"),
    ("Very Poor", "Very Poor"),
    ("Poor", "Poor"),
    ("Acceptable", "Acceptable"),
    ("Good", "Good"),
    ("Excellent", "Excellent")
]

class PracticeTypeFormCompletionQuestionnaire(models.Model):
    _name = 'practice.questionnaire'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Practice Type Form Completion Questionnaire'
    _rec_name = 'name_tutor'

    # Información relacionada con el estudiante y el centro
    practice_request_id = fields.Many2one(
        'practice.request',
        string="Practice Request",
        required=True
    )
    name_student = fields.Char(related="practice_request_id.name", string="Name of Student",store=True)
    course_id =  fields.Many2one(related="practice_request_id.course_id", string="Student")
    op_student_course_course_id = fields.Many2one(related="course_id.course_id",store=True)
    practice_center_id= fields.Many2one(related="practice_request_id.practice_center_id")
    tutor_id = fields.Many2one(related="practice_request_id.tutor_id",store=True)
    modality = fields.Many2one(related="practice_request_id.practice_center_type_id", string="Modality")
    number_hours_practice = fields.Float(related="practice_request_id.total_hours")

    campus = fields.Char('Campus')  # Aplica para modalidad presencial o athome
    # total_hours
    # Datos de áreas y especialidades
    area = fields.Char('Area')
    specialty_clinical_psychology = fields.Char('Specialty: Clinical Psychology')
    specialty_psychology_child_youth = fields.Char('Specialty: Child and Youth')
    specialty_psychology_third_generation = fields.Char('Specialty: Third Generation')

    # Información sobre programas de maestría
    master_psychology_face_to_face = fields.Char('Master Psychology Face to Face')
    master_psychology_at_home = fields.Char('Master Psychology At Home')
    master_psychology_online = fields.Char('Master Psychology Online')
    master_neuroscience_face_to_face = fields.Char('Master Neuroscience Face to Face')
    master_neuroscience_at_home = fields.Char('Master Neuroscience At Home')
    master_neuroscience_online = fields.Char('Master Neuroscience Online')
    master_education_face_to_face = fields.Char('Master Education Face to Face')
    master_education_online = fields.Char('Master Education Online')
    master_education_at_home = fields.Char('Master Education At Home')
    master_speech_therapy_face_to_face = fields.Char('Master Speech Therapy Face to Face')
    master_speech_therapy_online = fields.Char('Master Speech Therapy Online')
    master_speech_therapy_at_home = fields.Char('Master Speech Therapy At Home')

    # Valoraciones generales
    assessment_1 = fields.Selection(ratings,'A1. Service Presentation (Information, Documentation)')
    assessment_2 = fields.Selection(ratings,'A2. Practice Coordination by ISEP')
    assessment_3 = fields.Selection(ratings,'A3. Support During Practice Process by ISEP')
    assessment_14 = fields.Integer('A4. Relation of Practices with Program Content')
    assessment_15 = fields.Integer('A5. Opportunity to Broaden Knowledge')
    assessment_16 = fields.Integer('A6. Valid Experience for Job Search')
    assessment_17 = fields.Integer('A7. Fulfillment of Expectations')
    assessment_18 = fields.Selection(ratings,'A8. Overall Practice Evaluation')

    # Valoraciones específicas (online)
    typology_practices = fields.Char('Typology of Practices')
    assessment_4 = fields.Selection(ratings,'B1. Virtual Environment')
    assessment_5 = fields.Selection(ratings,'B2. Information: Presentation, Methodology, Calendar, Guide')
    assessment_6 = fields.Selection(ratings,'B3. Materials: Videos, Reflection Questions, Other Resources')
    assessment_7 = fields.Selection(ratings,'B4. Communication Tools: Forums, Online Clinical Sessions')
    assessment_8 = fields.Selection(ratings,'B5. Tutor: Responsiveness, Quality, Engagement')

    # Valoraciones específicas (centro externo)
    name_center_practice = fields.Char('Practice Center')
    assessment_9 = fields.Selection(ratings,'C1. Center: Facilities, Location, Services')
    assessment_10 = fields.Selection(ratings,'C1. Practice Tutor: Support, Guidance')
    assessment_11 = fields.Selection(ratings,'C1. Tasks Performed')
    assessment_12 = fields.Selection(ratings,'C1. Student Contribution to Center Activities')

    # Información adicional
    name_tutor = fields.Char('Name of Tutor')
    performed_hours = fields.Integer('Number of Hours Completed')

    observations = fields.Text('Observations')
    observations_suggestions = fields.Text('Suggestions and Observations')
    terms = fields.Char('Terms and Conditions')

    # assessment_1_numeric = fields.Integer(
    #     string="Numeric Assessment 1",
    #     compute="_compute_numeric_assessments",
    #     store=True
    # )
    #
    # @api.depends('assessment_1')
    # def _compute_numeric_assessments(self):
    #     ratings_map = {
    #         "NR": 0,
    #         "Very Poor": 1,
    #         "Poor": 2,
    #         "Acceptable": 3,
    #         "Good": 4,
    #         "Excellent": 5,
    #     }
    #     for record in self:
    #         record.assessment_1_numeric = ratings_map.get(record.assessment_1, 0)