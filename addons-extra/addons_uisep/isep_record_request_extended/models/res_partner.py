from odoo import fields, models, api
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'


    accepted_percentage = fields.Float(
        string="Documentos Aceptados",
        compute="_compute_accepted_percentage",
        store=True
    )

    @api.depends('ir_attachment_ids.state','ir_attachment_ids')
    def _compute_accepted_percentage(self):
        for partner in self:
            total_attachments = len(partner.ir_attachment_ids)
            if total_attachments > 0:
                accepted_attachments = len(partner.ir_attachment_ids.filtered(lambda a: a.state == 'accepted'))
                partner.accepted_percentage = (accepted_attachments / total_attachments)
            else:
                partner.accepted_percentage = 0.0
