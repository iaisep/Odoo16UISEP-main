# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError


class isep_form_data_wizard(models.TransientModel):
    _name = 'isep.form.data.wizard'

    sale_order_id = fields.Many2one('sale.order')
    order_start_url = fields.Char('Order URL')

    def default_get(self, fields):
        base_url = self.get_base_url()
        c = super(isep_form_data_wizard, self).default_get(fields)
        sale_order_id = self._context['get_sale_order_id']
        order_start_url = self._context['get_token']
        c['sale_order_id'] = sale_order_id
        c['order_start_url'] = ('/').join((base_url,"card", order_start_url))
        return c
