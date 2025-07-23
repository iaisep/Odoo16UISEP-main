import logging
from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class OpCourse(models.Model):
    _inherit = 'op.course'    

    product_template_id = fields.Many2one('product.template', string="Producto")
    