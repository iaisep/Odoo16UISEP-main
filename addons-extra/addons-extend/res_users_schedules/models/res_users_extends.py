# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class res_users_extends(models.Model):
    _inherit = 'hr.employee'

    schedules_ids = fields.One2many(
        'res.users.schedules',
        'user_id')
    is_schedules = fields.Boolean(string='Habilitar Horarios')
    


    