# -*- coding: utf-8 -*-
import pytz
import logging

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)


class op_session_wizard(models.TransientModel):
    _name = 'op.session.wizard'

    name = fields.Char(compute='_compute_name', string='Name', store=True)
    faculty_id = fields.Many2one('op.faculty', string='Profesor', required=True)
    admission_id = fields.Many2one('op.admission.register', string='Admision')
    course_id = fields.Many2one('op.course', string='Curso', required=True)
    subject_id = fields.Many2one('op.subject', string='Tema', required=True)
    time_url_metting = fields.Char(string='URL clase virtual')
    type_day = fields.Char(string='Día', compute='_compute_day', store=True)
    # batch_id = fields.Many2one('op.batch', string='Grupo')
    batch_ids = fields.Many2many(comodel_name='op.batch', string='Grupo')
    classroom_id = fields.Many2one('op.classroom', string='Aula')
    start_datetime = fields.Datetime(string='Session Time', default=lambda self: fields.Datetime.now(), required=True)
    end_datetime = fields.Datetime(required=True)


    @api.depends('faculty_id', 'subject_id', 'start_datetime')
    def _compute_name(self):
        # tz = pytz.timezone(self.env.user.tz)
        user_tz = self.env.user.tz if isinstance(self.env.user.tz, str) else 'UTC'

        # Comprobar si la zona horaria es válida en pytz
        try:
            tz = pytz.timezone(user_tz)
        except pytz.UnknownTimeZoneError:
            # Si la zona horaria no es válida, usar UTC como fallback
            tz = pytz.timezone('UTC')

        for session in self:
            if session.faculty_id and session.subject_id \
                    and session.start_datetime and session.end_datetime:
                session.name = \
                    session.faculty_id.name + ':' + \
                    session.subject_id.name + ':' + str(
                        session.start_datetime.astimezone(tz).strftime('%I:%M%p')) + '-' + str(
                        session.end_datetime.astimezone(tz).strftime('%I:%M%p'))



    @api.depends('start_datetime')
    def _compute_day(self):
        days = {0: 'monday', 1: 'tuesday', 2: 'wednesday', 3: 'thursday', 4: 'friday', 5: 'saturday', 6: 'sunday'}
        for record in self:
            record.type_day = days.get(record.start_datetime.weekday()).capitalize()
            # record.days = days.get(record.start_datetime.weekday())


    @api.constrains('start_datetime', 'end_datetime')
    def _check_date_time(self):
        if self.start_datetime > self.end_datetime:
            raise ValidationError(_(
                'End Time cannot be set before Start Time.'))


    
    @api.onchange('admission_id')
    def _onchange_admision_id(self):

        unique_batch_ids = set()
        admissions = self.env['op.admission'].sudo().search([
            ('register_id', '=', self.admission_id.id)            
            ])
        
        for admission in admissions:
            self.course_id = admission.course_id.id
            if admission.batch_id:
                unique_batch_ids.add(admission.batch_id.id)
                
        self.batch_ids = [(6, 0, list(unique_batch_ids))]


    
    def action_execute(self):
        session = self.env['op.session']

        for batch in self.batch_ids:
            session.create({
                'name': self.name,
                'faculty_id': self.faculty_id.id,
                'course_id': self.course_id.id,
                'subject_id': self.subject_id.id,
                'time_url_metting': self.time_url_metting,
                'type': self.type_day,
                'classroom_id': self.classroom_id.id,
                'start_datetime': self.start_datetime,
                'end_datetime': self.end_datetime, 
                'batch_id': batch.id,
                
            })
        




    # @api.onchange('course_id')
    # def onchange_course(self):
    #     self.batch_id = False
    #     if self.course_id:
    #         subject_ids = self.env['op.course'].search([
    #             ('id', '=', self.course_id.id)]).subject_ids
    #         return {'domain': {'subject_id': [('id', 'in', subject_ids.ids)]}}

