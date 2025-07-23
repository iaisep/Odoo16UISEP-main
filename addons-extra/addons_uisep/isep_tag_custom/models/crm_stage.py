# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class CrmStage(models.Model):
    _inherit = "crm.stage"

    tag_crm_id = fields.Many2one(
        'crm.tag',
        string="Etiqueta CRM",
        ondelete="set null",
        help="Etiqueta CRM asociada a esta etapa"
    )