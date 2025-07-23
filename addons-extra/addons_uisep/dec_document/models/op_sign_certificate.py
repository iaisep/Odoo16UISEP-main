# -*- coding: utf-8 -*-
from odoo import _, api, fields, models, tools

class Certificate(models.Model):
    _inherit = 'op.sign_certificate'
    _description = 'Certificate for Student Certificates'
    _order = "date_start desc, id desc"

    dec_certificate= fields.Boolean(
        string='DEC (SEP)',
        help='Si se habilita se utilizará para sellar los certificados DEC')

