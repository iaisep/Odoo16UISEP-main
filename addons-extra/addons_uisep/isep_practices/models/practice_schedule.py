# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class PracticeSchedule(models.Model):
    _name = 'practice.schedule'
    _description = 'PracticeSchedule'

    name = fields.Char('Name', compute="_compute_day", store=True)
    turn = fields.Selection([
        ('morning', 'Mañana'),
        ('afternoon', 'Tarde'),
        ('both', 'Mañana/Tarde'),
    ], 'Turn')
    practice_schedule_days_ids = fields.One2many('practice.schedule.days', 'practice_schedule_id')

    _sql_constraints = [
        ('unique_name',
         'unique(name)',
         'Day must be unique per schedule!'),
    ]


    def getTurn(self):
        return dict(self._fields['turn'].selection).get(self.turn)

    # @api.one
    @api.depends('practice_schedule_days_ids.day', 'turn')
    def _compute_day(self):
        joins = ', '.join(days.getDay() for days in self.practice_schedule_days_ids)
        replace1 = joins.replace(",", '')
        replace_total = replace1.replace("'", '')
        _days = replace_total.split()

        order = {'Lunes': 0, 'Martes': 1, 'Miercoles': 2, 'Jueves': 3, 'Viernes': 4, 'Sabado': 5}
        order_day = []

        for d in _days:
            valor = order[d]
            order_day.append((valor, d))
        order_day.sort()
        or_d = dict(order_day)
        total_day = [day for day in or_d.values()]
        self.name = ', '.join(total_day)
        if self.name and self.turn:
            self.name = self.name + ' - ' + str(self.getTurn())

    @api.onchange('practice_schedule_days_ids')
    def _validation_schedule_day(self):
        validate_day = {'monday': 0, 'tuesday': 0, 'wednesday': 0, 'thursday': 0, 'friday': 0, 'saturday': 0}
        for days in self.practice_schedule_days_ids:
            if days.day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']:
                validate_day[days.day] += 1
            if validate_day[days.day] > 1:
                raise ValidationError(
                    _("Day exist"))