from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    num_day = fields.Integer('Número de días para la creación de factura', config_parameter='num_day')