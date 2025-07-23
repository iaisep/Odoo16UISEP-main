
# -*- coding: utf-8 -*-
from odoo import fields, models, api, _

class MailParserConfig(models.Model):
    _name = 'mail.parser.config'
    _description = 'Configuración del Parser de Correo'
    _order='sequence'

    name = fields.Char(string='Nombre')
    sequence = fields.Integer('Sequence', default=100,help="Gives the sequence order when displaying.")
    reference = fields.Char(string="Referencia")
    tag = fields.Char(string='Etiqueta HTML', default="None")
    attribute = fields.Char(string='Atributo', default="None")
    attribute_value = fields.Char(string='Valor del Atributo', default="None")
    note = fields.Text(string="Notas")


    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            ref = vals.get('reference', '')
            tag = vals.get('tag', '')
            attribute = vals.get('attribute', '')
            attribute_value = vals.get('attribute_value', '')
            vals['name'] = f"{ref} / ({tag}, {{{attribute}: {attribute_value}}})" or _('New')        
        res = super(MailParserConfig, self).create(vals)
        return res