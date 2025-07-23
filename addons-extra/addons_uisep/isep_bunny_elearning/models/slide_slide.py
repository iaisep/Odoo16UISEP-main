# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
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


    nbr_bunny = fields.Integer("Number of Bunnys", store=True)


class Slide(models.Model):
    _inherit = 'slide.slide'

    nbr_bunny = fields.Integer("Number of Bunnys", store=True)


    slide_category = fields.Selection(
        selection_add=[('bunny', 'Bunny')], ondelete={'bunny': 'set default'})
    slide_type = fields.Selection(
        selection_add=[('bunny', 'Bunny')], ondelete={'bunny': 'set null'}, compute="_compute_slide_type", store=True)
    
    bunny_url = fields.Char('Bunny Direct Play URL')
    
    BUNNY_ID_REGEX = r'https:\/\/iframe\.mediadelivery\.net\/play\/(\d+)\/([a-f0-9-]+)'


    @api.depends('slide_category', 'google_drive_id', 'video_source_type', 'youtube_id','bunny_url')
    def _compute_embed_code(self):
        res = super(Slide, self)._compute_embed_code()
        for rec in self:
            embed_code = rec.embed_code
            embed_code_external = rec.embed_code_external
           

            if rec.slide_category == 'bunny' and rec.bunny_url:
                match = re.search(self.BUNNY_ID_REGEX, rec.bunny_url)
                if match.group(1) and match.group(2):
                    embed_code = Markup('<iframe src="https://iframe.mediadelivery.net/embed/%s/%s" allowFullScreen="true" frameborder="0"></iframe>') % ( match.group(1), match.group(2))
                    embed_code_external = Markup('<iframe src="https://iframe.mediadelivery.net/embed/%s/%s" allowFullScreen="true" frameborder="0"></iframe>') % ( match.group(1), match.group(2))
                    
            rec.embed_code = embed_code
            rec.embed_code_external = embed_code_external
                
        return res
            

    @api.depends('slide_category', 'source_type', 'video_source_type')
    def _compute_slide_type(self):
        res = super(Slide, self)._compute_slide_type()
        for slide in self:
            if slide.slide_category == 'bunny':
                slide.slide_type = 'bunny'
        return res                


    