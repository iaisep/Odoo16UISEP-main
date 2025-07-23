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


class SlidePartnerRelation(models.Model):
    _inherit = 'slide.slide.partner'

    lms_session_info_ids = fields.One2many('lms.session.info', 'slide_partner_id', 'LMS Session Info')
    


class Channel(models.Model):
    """ A channel is a container of slides. """
    _inherit = 'slide.channel'


    nbr_scorm = fields.Integer("Number of Scorms", store=True)


class LmsSessionInfo(models.Model):
    _name = 'lms.session.info'

    name = fields.Char("Name")
    value = fields.Char("Value")
    slide_partner_id = fields.Many2one('slide.slide.partner')


class Slide(models.Model):
    _inherit = 'slide.slide'

    nbr_scorm = fields.Integer("Number of Scorms", store=True)


    slide_category = fields.Selection(
        selection_add=[('scorm', 'Scorm')], ondelete={'scorm': 'set default'})
    slide_type = fields.Selection(
        selection_add=[('scorm', 'Scorm')], ondelete={'scorm': 'set null'}, compute="_compute_slide_type", store=True)
    scorm_data = fields.Many2many('ir.attachment')
    filename = fields.Char('Ruta de archivo')
    scorm_version = fields.Selection([
        ('scorm11', 'Scorm 1.1/1.2'),
        ('scorm2004', 'Scorm 2004 Edition')
    ], default="scorm11")
    
    @api.depends('slide_category', 'google_drive_id', 'video_source_type', 'youtube_id')
    def _compute_embed_code(self):
        request_base_url = request.httprequest.url_root if request else False
        res = super(Slide, self)._compute_embed_code()
        for rec in self:
            embed_code = rec.embed_code
            embed_code_external = rec.embed_code_external
            base_url = request_base_url or rec.get_base_url()
            if base_url[-1] == '/':
                base_url = base_url[:-1]

            if rec.slide_category == 'scorm' and rec.scorm_data:
                embed_code = Markup('<iframe src="%s" allowFullScreen="true" frameborder="0"></iframe>') % (rec.filename)
                embed_code_external = Markup('<iframe src="%s" allowFullScreen="true" frameborder="0"></iframe>') % (rec.filename)
            """if rec.slide_category == 'scorm' and rec.scorm_data:
                
                user_name = self.env.user.name
                user_mail = self.env.user.login
                end_point = base_url + '/slides/slide'
                end_point = urllib.parse.quote(end_point, safe=" ")
                actor = "{'name': [%s], mbox: ['mailto':%s]}" % (user_name,user_mail)
                actor = json.dumps(actor)
                actor = urllib.parse.quote(actor)
                embed_code = Markup('<iframe src="%s?endpoint=%s&actor=%s&activity_id=%s" allowFullScreen="true" frameborder="0"></iframe>') % (rec.filename,end_point,actor,rec.id)
                embed_code_external = Markup('<iframe src="%s?endpoint=%s&actor=%s&activity_id=%s" allowFullScreen="true" frameborder="0"></iframe>') % (rec.filename,end_point,actor,rec.id)
            """
            rec.embed_code = embed_code
            rec.embed_code_external = embed_code_external
                
        return res
            

    @api.depends('slide_category', 'source_type', 'video_source_type')
    def _compute_slide_type(self):
        res = super(Slide, self)._compute_slide_type()
        for slide in self:
            if slide.slide_category == 'scorm':
                slide.slide_type = 'scorm'
        return res                


    @api.onchange('scorm_data')
    def _on_change_scorm_data(self):
        if self.scorm_data:
            if len(self.scorm_data) > 1:
                raise ValidationError(_("Solo se permite un paquete de scorm por diapositiva."))
            tmp = self.scorm_data.name.split('.')
            ext = tmp[len(tmp) - 1]
            if ext != 'zip':
                raise ValidationError(_("El archivo debe ser un archivo zip."))
            self.read_files_from_zip()
        else:
            if self.filename:
                folder_dir = self.filename.split('scorm')[-1].split('/')[-2]
                path = os.path.join(os.path.dirname(os.path.abspath(__file__)))
                target_dir = os.path.join(os.path.split(path)[-2],"static","media","scorm",str(self.id),folder_dir)
                if os.path.isdir(target_dir):
                    shutil.rmtree(target_dir)

    
    def read_files_from_zip(self):
        file = base64.decodebytes(self.scorm_data.datas)
        fobj = tempfile.NamedTemporaryFile(delete=False)
        fname = fobj.name
        fobj.write(file)
        zipzip = self.scorm_data.datas
        f = open(fname, 'r+b')
        f.write(base64.b64decode(zipzip))
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)))
        with zipfile.ZipFile(fobj, 'r') as zipObj:
            listOfFileNames = zipObj.namelist()
            html_file_name = ''
            html_file_name = list(filter(lambda x: 'index.html' in x, listOfFileNames))
            if not html_file_name:
                html_file_name = list(filter(lambda x: 'index_lms.html' in x, listOfFileNames))
                if not html_file_name:
                    html_file_name = list(filter(lambda x: 'story.html' in x, listOfFileNames))
            
            source_dir = os.path.join(os.path.split(path)[-2],"static","media","scorm",str(self.id))
            zipObj.extractall(source_dir)
            self.filename = '/isep_scorm_elearning/static/media/scorm/%s/%s' % (str(self.id), html_file_name[0] if len(html_file_name) > 0 else None)
        f.close()