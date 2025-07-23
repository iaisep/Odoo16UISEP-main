from odoo import api, fields, models, Command
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class SaleOrderStage(models.Model):
    _inherit = 'sale.order.stage'

    
    custom_cron = fields.Boolean(string="Cobrar facturas en cron personalizado.")