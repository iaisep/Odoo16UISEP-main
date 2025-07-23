from odoo import http
from odoo.http import request
from datetime import datetime

class DownConsultController(http.Controller):

    @http.route('/downconsult/survey/<string:token>', type='http', auth='public', website=True)
    def survey_form(self, token, **kwargs):
        consult = request.env['admission.downconsult'].sudo().search([
            ('access_token', '=', token),
            ('token_expiration', '>', datetime.now())
        ], limit=1)

        if not consult:
            return request.render('isep_elearning_custom.token_expired_template')

        return request.render('isep_elearning_custom.downconsult_survey_template', {
            'consult': consult,
            'token': token
        })



    @http.route('/downconsult/submit', type='http', auth='public', website=True, csrf=False)
    def submit_survey(self, **post):
        consult = request.env['admission.downconsult'].sudo().browse(int(post.get('consult_id')))
        if not consult.exists() or consult.access_token != post.get('token'):
            return request.render('isep_elearning_custom.token_expired_template')

        try:
            consult.write({
                'description': post.get('general_comment', '')
            })

            for line in consult.question_line_ids:
                line.write({
                    'rating': post.get(f'rating_{line.id}', False)
                })

            consult.action_mark_done()

            consult.write({'access_token': False})

            return request.render('isep_elearning_custom.survey_thankyou_template')
        
        except Exception as e:
            return request.render('isep_elearning_custom.error_template', {'error': str(e)})