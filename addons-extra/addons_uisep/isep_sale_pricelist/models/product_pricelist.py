# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'
    
    def action_show_product_pricelist(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("isep_sale_pricelist.sale_product_pricelist_action")        
        action['domain'] = [('pricelist_id', '=', self.id)] 
        action['target'] = 'current'
        return action
        