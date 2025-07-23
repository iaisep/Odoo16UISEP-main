# -*- coding: utf-8 -*-

import uuid
from odoo import models, fields, api, _

class res_card_extends(models.Model):
    _name = 'res.card'

    def _get_default_access_token(self):
        return str(uuid.uuid4())
    
    @api.depends('month', 'year')
    def _get_date_expiration(self):
        for rec in self:
            rec.date_expiration = '%s/%s' %(rec.month, rec.year)
        


    partner_id = fields.Many2one('res.partner')
    partner = fields.Char(string='Cliente')
    name = fields.Char(string='Titular')
    number_target = fields.Char(string='Número de tarjeta')
    csv = fields.Char(string='CSV')
    date_expiration = fields.Char(string='Fecha de Caducidad', compute = _get_date_expiration)
    month = fields.Char(string='Mes')
    year = fields.Char(string='Año')
    access_token = fields.Char('Access Token', default=lambda self: self._get_default_access_token(), copy=False)
    active = fields.Boolean(default=False)
    use = fields.Boolean(default = False)




    

