# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import pytz
_logger = logging.getLogger(__name__)


class OpSession(models.Model):
    _inherit = 'op.session'

    faculty_name = fields.Char('Nombre del Profesor', related='faculty_id.name')
    course_name = fields.Char('Nombre del Curso', related='course_id.name')
    subject_name = fields.Char('Nombre del Tema', related='subject_id.name')

    slide_channel_id = fields.Many2one('slide.channel', string="Asignatura en Elearning",related='subject_id.slide_channel_id', store=True)
    slide_channel_num = fields.Integer('ID de Elearning', compute="compute_slide_channel_int", store=True)
    start_date = fields.Date(string="Fecha")

    @api.depends('slide_channel_id')
    def compute_slide_channel_int(self):
        for record in self:
            slide_channel_num = 0
            if record.slide_channel_id:
                slide_channel_num = record.slide_channel_id.id
            record.slide_channel_num = slide_channel_num

    @api.depends('faculty_id', 'subject_id', 'start_datetime')
    def _compute_name(self):
        tz = pytz.timezone(self.env.user.tz)
        for session in self:
            if session.faculty_id and session.subject_id \
                    and session.start_datetime and session.end_datetime:
                session.name = \
                    session.subject_id.name 
