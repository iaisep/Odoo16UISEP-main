from odoo import _, api, fields, models


class OpCourse(models.Model):
    _inherit = "op.course"

    modality = fields.Selection(selection=[('manual','Manual'),('auto','Automática')] , string="Modalidad", default='manual', required = True)
