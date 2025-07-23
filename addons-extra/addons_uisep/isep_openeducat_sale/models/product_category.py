import logging
from odoo import models, fields, api
from odoo.exceptions import UserError


class ProductCategory(models.Model):
    _inherit = 'product.category'

    code = fields.Char(string='Prefijo para Grupo')