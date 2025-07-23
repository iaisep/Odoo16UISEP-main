from odoo import models, fields
from odoo.exceptions import UserError

class OpCourse(models.Model):
    _inherit = 'op.course'

    include_txt = fields.Boolean(string="Incluir TXT para IA", help="Genera el contenido de Elearning en txt para la IA", index=True)
    