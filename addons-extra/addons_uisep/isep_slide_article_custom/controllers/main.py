from odoo import http
from odoo.http import request

class SlideController(http.Controller):

    @http.route('/slides/slide/get_slide_data_custom', type='json', auth='user', website=True)
    def get_slide_data(self, slide_id):
        slide = request.env['slide.slide'].sudo().browse(slide_id)
        if not slide.exists():
            return {
                'error': 'Slide not found'
            }

        return {
            'msn_custom': bool(slide.msn_custom),
        }

    


class CustomPageController(http.Controller):

    @http.route('/call/academic', type='http', auth='user', website=True)
    def custom_page(self, **kwargs):
        return request.render('isep_slide_article_custom.website_call_academic_tutor', {})
