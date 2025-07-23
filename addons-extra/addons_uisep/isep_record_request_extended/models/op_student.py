from odoo import fields, models, api
from odoo.exceptions import ValidationError


class OpStudent(models.Model):
    _inherit = 'op.student'


    accepted_percentage = fields.Float(
        string="Documentos Aceptados",
        related="partner_id.accepted_percentage",
        readonly=True
    )

    ir_attachment_ids = fields.One2many(related='partner_id.ir_attachment_ids', comodel_name='ir.attachment', string='Attachments')