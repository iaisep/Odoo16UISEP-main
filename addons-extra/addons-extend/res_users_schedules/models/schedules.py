# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class res_users_schedules(models.Model):
    _name = 'res.users.schedules'

    LIST_DAY =  [
        ('Monday',_('Monday')),
        ('Tuesday',_('Tuesday')),
        ('Wednesday',_('Wednesday')),
        ('Thursday',_('Thursday')),
        ('Friday',_('Friday')),
        ('Saturday',_('Saturday')),
        ('Sunday',_('Sunday')),
    ]

    user_id = fields.Many2one('hr.employee', string="User")
    day_selected = fields.Selection(LIST_DAY, string="Day")
    entry_time = fields.Float(string="Entry Time")
    departure_time = fields.Float(string="Departure Time")


    def write(self, vals):
        res = super(res_users_schedules, self).write(vals)
        if self.departure_time > 23.00 or self.entry_time > 23.00:
            raise UserError('El rango de hora es 0:00 a 23:00')
        elif self.departure_time < self.entry_time:
            raise UserError('Hora de salida tiene que ser mayor a la hora de entrada')
        return res
    
    
    @api.model
    def create(self, values):
        res = super(res_users_schedules, self).create(values)
        if res.departure_time > 23.00 or res.entry_time > 23.00:
            raise UserError('El rango de hora es 0:00 a 23:00')
        elif res.departure_time < res.entry_time:
            raise UserError('Hora de salida tiene que ser mayor a la hora de entrada')
        return res


    


    