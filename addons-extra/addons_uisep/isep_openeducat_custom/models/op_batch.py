import logging
from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class OpBatch(models.Model):
    _inherit = 'op.batch'

    tutor_id = fields.Many2one('res.users', 'Tutor de Orientación')
    professor_id = fields.Many2one('res.users', 'Tutor de Académico')

    teams_domain = fields.Char('Dominio de teams')    
    teams_link = fields.Char('Enlace de inducción')
    teams_msg = fields.Html('Mensaje para teams')


