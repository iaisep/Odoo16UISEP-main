# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class SurveyUserInputChannel(models.Model):
    _inherit = 'survey.user_input'

    active_lib=fields.Boolean("Envio a libreta", related='survey_id.active_lib')


    def cron_survey_send_library(self):
        surveys = self.search([
            ('active_ia', '=', True),
            ('active_lib', '=', True),
            ('survey_type', '=', 'assignment'),
            ('resumen_ia', '!=', ''),
            # ('comment', '=', ''),
            ('state', '=', 'done'),
            ('gradebook_student_id', '=', False),
            ])
        for survey in surveys:
            # try:
            if survey.user_input_line_ids:
                survey.update_answer_scores()
                survey.send_result()
            # except Exception as e:
            #     _logger.error(f"Error procesando la encuesta {survey.id}: {e}")