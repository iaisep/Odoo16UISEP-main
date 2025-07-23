from odoo import _, api, fields, models


class OpCourse(models.Model):
    _inherit = "op.course"

    faculty_id = fields.Many2one('op.department', string="Facultad")
