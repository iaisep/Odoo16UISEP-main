

# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from datetime import date

from odoo.addons.website_slides.controllers.main import WebsiteSlides

class CustomWebsiteSlides(WebsiteSlides):
    @http.route([
        '/slides/<model("slide.channel"):channel>',
        '/slides/<model("slide.channel"):channel>/page/<int:page>',
        '/slides/<model("slide.channel"):channel>/tag/<model("slide.tag"):tag>',
        '/slides/<model("slide.channel"):channel>/tag/<model("slide.tag"):tag>/page/<int:page>',
        '/slides/<model("slide.channel"):channel>/category/<model("slide.slide"):category>',
        '/slides/<model("slide.channel"):channel>/category/<model("slide.slide"):category>/page/<int:page>',
    ], type='http', auth="public", website=True, sitemap=WebsiteSlides.sitemap_slide)
    def channel(self, channel, category=None, tag=None, page=1, slide_category=None, uncategorized=False, sorting=None, search=None, **kw):
        is_internal_user = request.env.user.has_group('base.group_user')
        if not is_internal_user:
            partner = request.env.user.partner_id            
            admissions = request.env['op.admission'].sudo().search([('partner_id','=',partner.id)])
            # highest_date =  max(admissions.batch_id.mapped('end_date'))
            today = date.today()
            highest_date = False
            batch_id = False
            for ad in admissions:
                if ad.batch_id and ad.batch_id.end_date:
                    if not highest_date or ad.batch_id.end_date > highest_date:
                        highest_date = ad.batch_id.end_date
                        batch_id = ad.batch_id.id                    
                        
            if not highest_date or today > highest_date:
                if batch_id:
                    url = '/warning/batch/%s' % batch_id
                    return request.redirect(url)
                
        return super(CustomWebsiteSlides, self).channel(channel,category=category, tag=tag, page=page, slide_category=slide_category, uncategorized=uncategorized,sorting=sorting,search=search, **kw)


class OpWarningBatchController(http.Controller):
    
        
    @http.route('/warning/batch/<string:lot>', type='http',  methods=['GET', 'POST'], csrf=False, auth='user', website=True)
    def op_warning_batch(self, lot):
        batch_sudo = request.env['op.batch'].sudo().browse(int(lot))
        name = batch_sudo.name
        

        start_date = batch_sudo.start_date
        end_date = batch_sudo.end_date
        
        start_date = start_date.strftime('%d-%m-%Y')        
        end_date = end_date.strftime('%d-%m-%Y')      

        return http.request.render('isep_elearning_custom.template_restrict_batch', {
            'name': name,
            'start_date': start_date,
            'end_date': end_date,
        })