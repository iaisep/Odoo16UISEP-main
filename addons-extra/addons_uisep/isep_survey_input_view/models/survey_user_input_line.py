import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class SurveyUser_inputLine(models.Model):
    _inherit = 'survey.user_input.line'

    
    survey_type = fields.Selection(
        string='Tipo',
        selection=[('survey', 'Encuesta'), ('cert', 'Certificación'),('exam', 'Examen'),('assignment', 'Asignación')] ,  store=True, related="survey_id.survey_type"
    )
    op_subject_id = fields.Many2one('op.subject', string="Asignatura", store=True, related="user_input_id.op_subject_id" )
    course_id = fields.Many2one('op.course', string="Curso",   store=True, related="user_input_id.course_id" )
    batch_id = fields.Many2one('op.batch', string="Grupo",   store=True, related="user_input_id.batch_id" )
    

