# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ProductTemplate(models.Model):
    _inherit = "product.template"

    tag_crm_id = fields.Many2one(
        'crm.tag',
        string="Etiqueta CRM",
        ondelete="set null",
        help="Etiqueta CRM asociada a este producto"
    )

    tag_crm_id_interes = fields.Many2one(
        'crm.tag',
        string="Etiqueta CRM interés",
        ondelete="set null",
        help="Etiqueta CRM asociada a este producto para interés alumnos"
    )

    tag_crm_id_confirm = fields.Many2one(
        'crm.tag',
        string="Etiqueta CRM Confirmación",
        ondelete="set null",
        help="Etiqueta CRM asociada a esta plantilla de producto para confirmación de alumnos"
    )