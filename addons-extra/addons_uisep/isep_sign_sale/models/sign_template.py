# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class sign_templates_extends(models.Model):
    _inherit = 'sign.template'

    sale_id = fields.Many2one('sale.order', string="Sale Matrícula ID", required=True, index=True, copy=False)
    


    