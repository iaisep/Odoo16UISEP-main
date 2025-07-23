
# -*- coding: utf-8 -*-
from odoo import fields, models, _

class ModelsConfigConsul(models.Model):
    _name = 'models.config.consul'
    _description = 'Configuración modulos a consultar IA'
    _order='id asc'

    name = fields.Char(string='Nombre')
    question_search = fields.Char(string='Observacion', help='Pregunta clave que podria decir el usuario relacionada a esta tabla' )    
    model_id = fields.Many2one('ir.model', string='Modelo', help='Escoja un modelo para consultar atravez de la IA, OJO asegurese de que el modelo tienen partner_id') 
    rel_field_id = fields.Many2one('ir.model.fields', string='Campo partner a relacionar', help='Coloque el campo partner_id relacionado para la busqueda, tome nota que este campo puede cambiar dependiendo del modelo')   
    state_field_id = fields.Many2one('ir.model.fields', string='Campo estado a relacionar', help='Coloque el Estado, del modelo destino a consultar de ser necesario') 
    state_content =  fields.Char(string='Estado de modelo', help='Coloque el estado TECNICO del campo estado.') 
    config_consul_line_ids = fields.One2many('models.config.consul.line', 'config_consul_id', string = "detalles", required=False, index=True,readonly=False,copy=False )
    other_filter = fields.Boolean(string='Crear otro filtro', help='Activar para crear otro filtro si es necesario')
    filter_field_id = fields.Many2one('ir.model.fields', string='Otro filtro', help='Coloque un campo que desee  filtrar') 
    filter_content =  fields.Char(string='Filtro del modelo', help='Coloque el estado TECNICO del campo, contenido del campo o si es un Many2one el ID.') 
    


class ModelsConfigConsulLine(models.Model):
    _name = 'models.config.consul.line'

    name = fields.Char(string='Nombre columna', copy=False, required=True)
    config_consul_id = fields.Many2one('models.config.consul', string='Configuración modulos a consultar IA',requerid=True, ondelete="cascade", index=True)
    fields_ids = fields.Many2one('ir.model.fields', string="Campo")
    model_field = fields.Char(related='fields_ids.relation')
    followone_field_id = fields.Many2one('ir.model.fields',string='Complemento campo', help='Coloque la continuacion si es un campo que solo es relacionado en su primer nivel, si no corresponde deje vacio')
    model2_field = fields.Char(related='followone_field_id.relation')
    followtwo_field_id = fields.Many2one('ir.model.fields',string='Complemento campo', help='Coloque la continuacion si es un campo que solo es relacionado en su segundo nivel, si no corresponde deje vacio')
    sequence = fields.Integer('Sequence', default=100,help="Mueva el orden de las filas")
