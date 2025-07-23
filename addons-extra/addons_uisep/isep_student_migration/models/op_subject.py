# -*- coding: utf-8 -*-
from odoo import models, fields


class OpSubject(models.Model):
    _inherit = 'op.subject'

    is_imported_record = fields.Boolean(default=False, string='¿Es registro importado de Odoo 12?')
