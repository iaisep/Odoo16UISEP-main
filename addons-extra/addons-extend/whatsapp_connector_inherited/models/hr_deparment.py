from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class Department(models.Model):
    _inherit = "hr.department"

    is_coordinator = fields.Boolean(string="is_coordinator", default=False)