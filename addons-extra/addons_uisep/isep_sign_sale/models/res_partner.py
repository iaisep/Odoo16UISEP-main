# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class res_partner_extends(models.Model):
    _inherit = 'res.partner'
    
    university = fields.Char(string='Universidad')
    profession = fields.Char(string='Profesion')
    titulacion = fields.Char(string='Titulación')
    finalizacionestudios = fields.Date(string='Finalización de Estudios')
