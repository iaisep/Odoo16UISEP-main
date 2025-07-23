# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request
from odoo.addons.website_slides.controllers.main import WebsiteSlides


class WebsiteSlidesExternalVideo(WebsiteSlides):

    @http.route('/slide/slide/set_session_video_info', type='json', auth="user", website=True)
    def _set_session_video_info(self, slide_id, element, value):
        slide_partner_sudo = request.env['slide.slide.partner'].sudo()
        slide_id = request.env['slide.slide'].browse(slide_id)
        slide_partner_id = slide_partner_sudo.search([
            ('slide_id', '=', slide_id.id),
            ('partner_id', '=', request.env.user.partner_id.id)], limit=1)
        if not slide_partner_id:
            slide_partner_id = slide_partner_sudo.create({
                'slide_id': slide_id.id,
                'channel_id': slide_id.channel_id.id,
                'partner_id': request.env.user.partner_id.id
            })
        
        

    @http.route('/slides/slide/set_completed_local_external', website=True, type="json", auth="public")
    def slide_set_completed_local_external(self, slide_id, completion_type):
        if request.website.is_public_user():
            return {'error': 'public_user'}
        fetch_res = self._fetch_slide(slide_id)
        slide = fetch_res['slide']
        if fetch_res.get('error'):
            return fetch_res
        if slide.website_published and slide.channel_id.is_member:
            slide.action_mark_completed()
        return {
            'channel_completion': fetch_res['slide'].channel_id.completion
        }
