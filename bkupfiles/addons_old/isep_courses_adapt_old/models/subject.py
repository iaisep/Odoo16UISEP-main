from datetime import date, datetime
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

class OpSubject(models.Model):
    _inherit = "op.subject"
    course_ids = fields.Many2many('op.course','op_curse_rel','subject_id',string='Cursos')
    moodle_id=fields.Char(string="Moodle ID")