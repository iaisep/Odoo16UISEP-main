# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class OpCourseType(models.Model):
    _inherit = "op.course.type"

    tag_crm_id = fields.Many2one(
        'crm.tag',
        string="Etiqueta CRM",
        ondelete="set null",
        help="Etiqueta CRM asociada a esta etapa"
    )

    tag_crm_id_confirm = fields.Many2one(
        'crm.tag',
        string="Etiqueta CRM Confirmación",
        ondelete="set null",
        help="Etiqueta CRM asociada a esta etapa"
    )

class OpCourseArea(models.Model):
    _inherit = "op.area.course"

    tag_crm_id = fields.Many2one(
        'crm.tag',
        string="Etiqueta CRM",
        ondelete="set null",
        help="Etiqueta CRM asociada a esta etapa"
    )

    tag_crm_id_confirm = fields.Many2one(
        'crm.tag',
        string="Etiqueta CRM Confirmación",
        ondelete="set null",
        help="Etiqueta CRM asociada a esta etapa"
    )

    