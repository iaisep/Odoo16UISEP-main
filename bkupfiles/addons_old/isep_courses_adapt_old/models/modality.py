# -*- coding: utf-8 -*-

from odoo import models, fields


class OpModality(models.Model):
    _name = "op.modality"
    _description = "Modality"

    name = fields.Char('Name', size=128, required=True)
    code = fields.Char('Code', size=8, required=True)
    new_code = fields.Char('New code', size=8, required=True)
    analytic_code  = fields.Char('Analytic code', size=8)

    _sql_constraints = [
        ('unique_modality_code',
         'unique(code)', 'Code should be unique per modality!')]
