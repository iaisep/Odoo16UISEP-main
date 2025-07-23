# -*- coding: utf-8 -*-
import base64
import logging


from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime



from odoo import models, fields, api

class PracticeRequestDocument(models.Model):
    _name = 'practice.request.document'
    _description = 'Practice Request Document'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Document Name',  tracking=True)
    file = fields.Binary('File', required=True, tracking=True, attachment=True)
    file_name = fields.Char('File Name')
    description = fields.Text('Description')
    upload_date = fields.Datetime('Upload Date', default=fields.Datetime.now, tracking=True)
    practice_request_id = fields.Many2one(
        'practice.request',
        string='Practice Request',
        required=True,
        ondelete='cascade',
        tracking=True
    )
    document_type = fields.Selection(
        [('agreement', 'Agreement'),
         ('certificate', 'Certificate'),
         ('report', 'Report'),
         ('other', 'Other')],
        string='Document Type',
        required=True,
        tracking=True
    )
