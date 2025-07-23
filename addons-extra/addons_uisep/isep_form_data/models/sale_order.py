# -*- coding: utf-8 -*-

import uuid
from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__) 


class sale_order_extends(models.Model):
    _inherit = 'sale.order'

    card = fields.Boolean(default=False, string="Activar tarjeta")

    order_start_url = fields.Char('Tarjeta URL')


    def open_form(self):
        res_card_env = self.env['res.card']
        # obj_card_env = res_card_env.search([('partner_id','=',self.partner_id.id)])
        new_obj = res_card_env.create({
                'partner':self.partner_id.name,
                'partner_id': self.partner_id.id,
            })


        # if obj_card_env:
        #     new_obj = obj_card_env[0]
        # else:
        #     new_obj = res_card_env.create({
        #         'partner':self.partner_id.name,
        #         'partner_id': self.partner_id.id,
        #     })

        values = {
            'id':'isep_form_data_wizard_view',
            'name':u'Link tarjeta de Cliente',
            'view_type':'form',
            'view_mode':'form',
            'target':'new',
            'context':{
                'get_sale_order_id':self.id,
                'get_token':new_obj.access_token
            },
            'res_model':'isep.form.data.wizard',
            'type':'ir.actions.act_window',
        }

        return values


    def create(self, vals):
        sale_order = super(sale_order_extends, self).create(vals)
        
        base_url = self.get_base_url()

        res_card_env = self.env['res.card']
        new_obj = res_card_env.create({
            'partner': sale_order.partner_id.name,
            'partner_id': sale_order.partner_id.id,
        })

        sale_order.order_start_url = f"{base_url}/card/{new_obj.access_token}"
        
        return sale_order


    def write(self, vals):
        res = super(sale_order_extends, self).write(vals)

        if 'partner_id' in vals:
            for order in self:
                order._update_order_start_url()
                
        return res

    def _update_order_start_url(self):
        base_url = self.get_base_url()

        res_card_env = self.env['res.card']
        new_obj = res_card_env.create({
            'partner': self.partner_id.name,
            'partner_id': self.partner_id.id,
        })

        self.order_start_url = f"{base_url}/card/{new_obj.access_token}"
