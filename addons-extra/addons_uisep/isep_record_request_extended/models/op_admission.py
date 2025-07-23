from odoo import fields, models, api
from odoo.exceptions import ValidationError


class OpAdmission(models.Model):
    _inherit = 'op.admission'


    accepted_percentage = fields.Float(
        string="Documentos Aceptados",
        related="partner_id.accepted_percentage",
        readonly=True
    )
