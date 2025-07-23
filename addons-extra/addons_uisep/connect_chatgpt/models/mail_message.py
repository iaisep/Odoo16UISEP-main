# -*- coding: utf-8 -*-
from odoo import fields, models, _

class MailMessage(models.Model):
    _inherit= "mail.message"

    type_message_role = fields.Selection([
        ('assistant','Asistente IA'),
        ('user','Usuario')],string="Tipo mensaje", copy=False,default='user')