# -*- coding: utf-8 -*-
from odoo import fields, models,api ,_

class HelpdeskTeam(models.Model):
    _inherit= 'helpdesk.team'

    activate_gpt = fields.Boolean(string='Activar asistente IA', copy=False)
    consult_gpt = fields.Boolean(string='Consultar antes de enviar', copy=False, help='Active para evitar que se conteste de forma automatica GPT y pueda verlo primero el asesor antes de enviarse')
    token_gpt=fields.Char(string='Token', copy=False, help='Coloque aca el token api que proporciona OpenIA')
    url_gpt = fields.Char(string='Url', copy=False, help='Enlace al cual se conecta la API de OpenIA', default='https://api.openai.com/v1/chat/completions')
    temperature_gpt = fields.Float(string='Temperatura chat', copy=False, help='Configura como contestara la IA. ejemplo 0.15 ofrece una respuesta directa, 1.0 nos ofrece una respuesta creativa detallada y con recomendaciones', default='0.5')
    model_gpt = fields.Char(string='Modelo IA', copy=False, help='Tipo de modelo de inteligencia que se utilizara aca coloca el modelo entrenado', default='gpt-3.5-turbo')
    instructions_gpt = fields.Char(string='Instrucciones', help='Coloque una breve instruccion para el asistente', copy=False, default='You are a helpful assistant, in spanish,focus in question major')
    mail_parser_ids = fields.Many2many('mail.parser.config', string="Tag parser mail")
    max_tokens_gpt = fields.Integer(string='Maximo tokens', help='Refiere a la cantidad máxima de unidades de texto (tokens) que el modelo generará como respuesta a una entrada dada', default='800')
    finish_gpt_ids = fields.Many2many('helpdesk.finish.gpt',string='Tipo despedida', help='Despedida aproximada del usuario para cerrar el ticket', copy=False)
    stage_id = fields.Many2one('helpdesk.stage', string='Estado a cerrar', help='Estado que pasara cuando se detecte la despedida', copy=False)
    activate_autoclose = fields.Boolean(string='Autocerrado', help='Activar el auto cerrado de ticket colocando una automatizacion y tiempo establecido')
    days_auto = fields.Integer(string='Dias', help='Dias para cerrar automaticamente si el usuario no responde el hilo de IA', copy=False)
    config_consult_ids = fields.Many2many('models.config.consul', string='Modulo a consultar')
    article_embeding_ids = fields.Many2many('article.embedding', string='Art. Conocimiento a consultar', help='Articulos de conocimiento que se consultaran')
    consult_consult_gpt = fields.Boolean(string='Consultar modelos a enviar', copy=False, help='Active para visualizar la tablas consultadas en el ticket')
    slide_channel_ids = fields.Many2many('slide.channel', relation='gpt_helpdesk_team_slide_channel_rel',column1='team_id',column2='channel_id',string='Elearning a consultar', help='Cursos de Elearning que se consultaran')
    slide_slide_ids = fields.Many2many('slide.slide', string="Selecciona contenido",relation='gpt_helpdesk_team_website_slide_channel_rel',  column1='team_id',column2='website_channel_id', help='Contenido Elearning que se consultara')
    activate_autocancel = fields.Boolean(string='AutoCancel', help='Activar el auto cancelar de ticket colocando una automatizacion y tiempo establecido')
    stage_cancel_id = fields.Many2one('helpdesk.stage', string='Estado a Cancel', help='Estado a cambiar 48 horas despues si no contesta usuario', copy=False)

    @api.onchange('slide_channel_ids')
    def _onchange_slide_range(self):
        if self.slide_channel_ids:            
            slide_slide = self.env['slide.slide'].search([
                ('channel_id', 'in', self.slide_channel_ids.ids),
                ('create_text', '=', True),
            ])
            self.slide_slide_ids = [(6, 0, slide_slide.ids)]
        else:
            self.slide_slide_ids = [(5, 0)]

class HelpdeskStage(models.Model):
    _inherit= 'helpdesk.stage'

    acti_state_ia = fields.Boolean(string='Estado activa IA', help='Estado donde la IA enviara la respuesta automatizada', default=False, copy=False)


class HelpdeskFinishGpt(models.Model):
    _name= 'helpdesk.finish.gpt'

    name = fields.Char(string='Despedida usuario', help='Coloque la despedida que puede realizar el usuario',copy=False, required=True)

    @api.depends('name')
    def _compute_name_lowercase(self):
        for record in self:
            if record.name:
                record.name = record.name.lower()

    @api.model
    def create(self, values):
        if 'name' in values and values['name']:
            values['name'] = values['name'].lower()
        return super(HelpdeskFinishGpt, self).create(values)
    
    def write(self, values):
        if 'name' in values and values['name']:
            values['name'] = values['name'].lower()
        return super(HelpdeskFinishGpt, self).write(values)