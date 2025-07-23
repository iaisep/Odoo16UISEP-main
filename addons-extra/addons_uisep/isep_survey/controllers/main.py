from odoo import http
from odoo.http import request

class SlideController(http.Controller):

    @http.route('/slides/slide/get_slide_data_description', type='json', auth='user', website=True)
    def get_slide_data(self, slide_id):
        slide = request.env['slide.slide'].sudo().browse(slide_id)
        if not slide.exists():
            return {
                'error': 'Slide not found'
            }

        return {
            'slide_description': slide.description or '',
            'survey_description': (
                slide.survey_id.description
                if slide.survey_id.survey_type == 'assignment' and slide.survey_id.description
                else ''
            ),
        }

