import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class SurveySurvey(models.Model):
    _inherit = 'survey.survey'

    survey_type = fields.Selection(
        string='Tipo',
        selection=[('survey', 'Encuesta'), ('cert', 'Certificación'),('exam', 'Examen'),('assignment', 'Asignación')] , default="survey"
    )


    @api.model
    def create(self, values):
        res = super(SurveySurvey, self).create(values)    
        if res.survey_type in ('exam','assignment'):
            res.access_mode = 'token'
            res.users_login_required = True
            res.is_attempts_limited = True
            res.users_can_go_back = True
            res.certification = False
            res.scoring_type = 'no_scoring' if res.survey_type == 'assignment' else 'scoring_without_answers'
        return res
    

    def write(self, values):
        for survey in self:
            if 'survey_type' not in values:
                values['survey_type'] = survey.survey_type
            if values['survey_type'] in ('exam', 'assignment'):                
                values.update({
                    'access_mode': 'token',
                    'users_login_required': True,
                    'is_attempts_limited': True,
                    'users_can_go_back': True,
                    'certification': False,
                    'scoring_type': 'no_scoring' if values['survey_type'] == 'assignment' else 'scoring_without_answers'
                })
        return super(SurveySurvey, self).write(values)
    

class SurveyQuestion(models.Model):
    _inherit = 'survey.question'


    @api.model
    def create(self, values):
        res = super(SurveyQuestion, self).create(values)
        if res.survey_id.survey_type in ('exam', 'assignment'):
            res.constr_mandatory = True
        return res
    

    def write(self, values):
        for question in self:
            if question.survey_id.survey_type in ('exam', 'assignment'):
                values['constr_mandatory'] = True
        return super(SurveyQuestion, self).write(values)