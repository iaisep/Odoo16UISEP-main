from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    chat_department = fields.Many2one( 'hr.department',string="Departamento Chatroom?", groups="whatsapp_connector_inherited.group_chat_coordinator" )
