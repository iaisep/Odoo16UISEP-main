import logging
from odoo import http
from odoo.http import request
_logger = logging.getLogger(__name__)


class SurveyInh(http.Controller):


    @http.route('/survey/resultss/<string:survey_token>', type='http', auth='public', website=True)
    def survey_result(self, survey_token, **kw):
        survey_user_input = request.env['survey.user_input'].sudo().search([
            ('access_token', '=', survey_token)
            ], limit=1)
        if not survey_user_input:
            return request.not_found()

        answers = request.env['survey.user_input.line'].sudo().search([
            ('user_input_id', '=', survey_user_input.id)
            ])

        return request.render('isep_survey_question_result.result_survey_custom', {
            'survey': survey_user_input.survey_id,
            'answers': answers,
            })
            