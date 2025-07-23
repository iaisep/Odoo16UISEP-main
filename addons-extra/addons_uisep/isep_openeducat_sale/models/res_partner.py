import logging
from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'    

    gender = fields.Selection(
        [('m', 'Masculino'), ('f', 'Femenino'), ('o', 'Otro')],
        string='Género'
        )
    