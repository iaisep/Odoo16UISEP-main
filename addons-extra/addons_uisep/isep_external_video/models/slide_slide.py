# -*- coding: utf-8 -*-
import os
import json
import base64
import zipfile
import tempfile
import shutil
import urllib.parse
from werkzeug import urls
from odoo.http import request
from markupsafe import Markup
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.addons.http_routing.models.ir_http import url_for
import re



class Channel(models.Model):
    """ A channel is a container of slides. """
    _inherit = 'slide.channel'


    nbr_local_external = fields.Integer('Video Externo', store=True)

class Slide(models.Model):
    _inherit = 'slide.slide'

    nbr_local_external = fields.Integer("Video Externo", store=True)



    slide_category = fields.Selection(
                        selection_add=[('local_external', 'Local or External Video')],
                        ondelete={'local_external': 'cascade'})
    slide_category = fields.Selection(
        selection_add=[('local_external', 'Video Externo MP4')], ondelete={'local_external': 'set default'})
    slide_type = fields.Selection(
        selection_add=[('local_external', 'Video Externo MP4')], ondelete={'local_external': 'set null'}, compute="_compute_slide_type", store=True)
    
    external_url = fields.Char('URL externa')
    
    


    @api.depends('slide_category', 'google_drive_id', 'video_source_type', 'youtube_id','external_url','bunny_url')
    def _compute_embed_code(self):
        res = super(Slide, self)._compute_embed_code()
        for rec in self:
            embed_code = rec.embed_code
            embed_code_external = rec.embed_code_external
           

            if rec.slide_category == 'local_external' and rec.external_url:
                content_url = rec.external_url
                rec.embed_code = content_url

                
                embed_code = '<video class="local_video" controls controlsList="nodownload"><source src="' + content_url + '" type="video/mp4" /></video>'  #Markup('<video id="isep-player" class="video-js" controls><source src="%s" type="video/mp4" /></video>' % rec.external_url)
                embed_code_external = '<video class="local_video" controls controlsList="nodownload"><source src="' + content_url + '" type="video/mp4" /></video>'   # Markup('<video id="isep-player" class="video-js" controls><source src="%s" type="video/mp4"/></video>'  % rec.external_url)
                    
            rec.embed_code = embed_code
            rec.embed_code_external = embed_code_external
                
        return res
            

    @api.depends('slide_category', 'source_type', 'video_source_type')
    def _compute_slide_type(self):
        res = super(Slide, self)._compute_slide_type()
        for slide in self:
            if slide.slide_category == 'local_external':
                slide.slide_type = 'local_external'
        return res                


    