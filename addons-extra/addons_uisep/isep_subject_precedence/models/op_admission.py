import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date

_logger = logging.getLogger(__name__)

class OpAdmission(models.Model):
    _inherit = 'op.admission'

    
    modality = fields.Selection(selection=[('manual','Manual'),('auto','Automática')] , string="Modalidad", default=lambda r: r.course_id.modality or 'auto', required = True)

    @api.onchange('course_id')
    def update_modality(self):
        for admission in self:
            admission.modality = admission.course_id.modality

    def auto_enroll_student_auto(self):
        """ Automatiza la inscripción de los alumnos y desactiva registros si ha pasado la fecha de finalización. Permite enroll de materias sin fecha especificada"""
        today = date.today()        
        for record in self:
            if record.state == 'done':
                if not record.batch_id:
                    continue
                
                for subject_batch in record.batch_id.subject_to_batch_ids:
                    if not subject_batch.subject_id.slide_channel_id:
                        continue  
             
                    channel_partners = self.env['slide.channel.partner'].search([
                        ('partner_id', '=', record.partner_id.id),
                        ('channel_id', '=', subject_batch.subject_id.slide_channel_id.id),
                        ('batch_id', '=', record.batch_id.id),
                    ])

                    if (not subject_batch.date_from and not subject_batch.date_to) or subject_batch.date_from <= today <= subject_batch.date_to:
                        if channel_partners:
                            channel_partners.write({
                                'active': True,
                                'course_id': record.course_id.id,
                                'register_id': record.register_id.id,
                                'admission_id': record.id,
                                'date_from': subject_batch.date_from,
                                'date_to': subject_batch.date_to,
                            })
                        else:
                            self.env['slide.channel.partner'].create({
                                'active': True,
                                'channel_id': subject_batch.subject_id.slide_channel_id.id,
                                'partner_id': record.partner_id.id,
                                'course_id': record.course_id.id,
                                'batch_id': record.batch_id.id,
                                'date_from': subject_batch.date_from,
                                'date_to': subject_batch.date_to,
                                'op_subject_id': subject_batch.subject_id.id,
                                'register_id': record.register_id.id,
                                'admission_id': record.id,
                            })

                    elif today > subject_batch.date_to and channel_partners:
                        channel_partners.write({'active': False})


    def enroll_student(self):
        res = super().enroll_student()
        for record in self.filtered(lambda a: a.modality == 'auto'):
            record.auto_enroll_student_auto()
        return res

    def auto_enroll_student_subject(self, subject_id):
        """ Automatiza la inscripción de los alumnos en las materias que dependen de subject """
        today = date.today()        
        for record in self:
            if record.state == 'done':
                if not record.batch_id:
                    continue
                
                for subject_batch in record.batch_id.subject_to_batch_ids.filtered(lambda s: s.subject_id.parent_subject_id.id == subject_id):
                    if not subject_batch.subject_id.slide_channel_id:
                        continue  
                    channel_partners = self.env['slide.channel.partner'].search([
                        ('partner_id', '=', record.partner_id.id),
                        ('channel_id', '=', subject_batch.subject_id.slide_channel_id.id),
                        ('batch_id', '=', record.batch_id.id),
                    ])

                       
                    if (not subject_batch.date_from and not subject_batch.date_to) or subject_batch.date_from <= today <= subject_batch.date_to:
                        if channel_partners:
                            channel_partners.write({
                                'active': True,
                                'course_id': record.course_id.id,
                                'register_id': record.register_id.id,
                                'admission_id': record.id,
                                'date_from': subject_batch.date_from,
                                'date_to': subject_batch.date_to,
                            })
                        else:
                            self.env['slide.channel.partner'].create({
                                'active': True,
                                'channel_id': subject_batch.subject_id.slide_channel_id.id,
                                'partner_id': record.partner_id.id,
                                'course_id': record.course_id.id,
                                'batch_id': record.batch_id.id,
                                'date_from': subject_batch.date_from,
                                'date_to': subject_batch.date_to,
                                'op_subject_id': subject_batch.subject_id.id,
                                'register_id': record.register_id.id,
                                'admission_id': record.id,
                            })

                    elif today > subject_batch.date_to and channel_partners:
                        channel_partners.write({'active': False})


