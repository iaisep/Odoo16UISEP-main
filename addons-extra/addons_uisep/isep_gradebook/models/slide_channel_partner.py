# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
import logging

_logger = logging.getLogger(__name__)



class SlideChannelPartner(models.Model):
    _inherit = 'slide.channel.partner'

    # INTERACTION
    # def write(self, values):
    #     slide_channel_partner = super(SlideChannelPartner, self).write(values)
    #     for record in self:
    #         channel_id = record.sudo().channel_id
    #         partner_id = record.sudo().partner_id

    #         channel_partner_id = record.id
    #         admission_id = False
    #         op_subject_id = False
    #         course_id = False
    #         gradebook_subject = False
    #         # _logger.info('######### 01 #########################')
            
    #         channel_partner_id = record
    #         admission_id = channel_partner_id.sudo().admission_id
    #         op_subject_id = channel_partner_id.sudo().op_subject_id
    #         course_id = channel_partner_id.sudo().course_id

    #         # search_gradebook_subject(partner_id,admission_id,course_id,op_subject_id):
    #         if admission_id and op_subject_id and course_id and op_subject_id.subject_type == "compulsory":
    #             gradebook_subject = channel_partner_id.sudo().search_gradebook_subject(partner_id,admission_id,course_id,op_subject_id)
    #             # gradebook_subject devuelve {'gradebook_student_id': gradebook_student_id, 'gradebook_subject_id': gradebook_subject_id}

    #             gradebook_result_interaction = gradebook_subject['gradebook_subject_id'].sudo().gradebook_result_ids.filtered(lambda d: d.survey_type == 'interaction')
                
    #             # ANTES DE CREAR O ACTUALIZAR  DEBEMOS EVALUAR SI EXISTE FORO EN EL TEMPLATE DE GRADEBOOK
    #             gradebook = gradebook_subject['gradebook_subject_id'].gradebook_id or gradebook_subject['gradebook_student_id'].gradebook_id
    #             if 'interaction' in gradebook.gradebook_template_ids.mapped('type'):
    #                 if not gradebook_result_interaction:
    #                     application_number = admission_id.sudo().application_number
    #                     description = "%s - Interacción: %s" % (application_number, course_id.name)
    #                     data = {
    #                         'name': description,
    #                         'channel_id': channel_id.id,
    #                         'channel_partner_id': channel_partner_id.id,
    #                         'scoring_total': record.completion/10,
    #                         'gradebook_subject_id': gradebook_subject['gradebook_subject_id'].id,
    #                         'survey_type': 'interaction',
    #                         'description': description,
    #                     }
    #                     record.env['app.gradebook.result'].sudo().create(data)
    #                 else:
    #                     gradebook_result_interaction[0].scoring_total = record.completion/10
          
    #     return slide_channel_partner

    
    
    def search_gradebook_subject(self,partner_id,admission_id,course_id,op_subject_id):
        app_gradebook_student_model = self.env['app.gradebook.student']
        app_gradebook_subject_model = self.env['app.gradebook.subject']
        gradebook_student_id = app_gradebook_student_model.sudo().search([
            ('partner_id', '=', partner_id.id),
            ('admission_id', '=', admission_id.id),
            ('course_id', '=', course_id.id)
        ], limit=1)
        gradebook_subject_id = app_gradebook_subject_model.sudo().search([
            ('partner_id', '=', partner_id.id),
            ('admission_id', '=', admission_id.id),
            ('op_subject_id', '=', op_subject_id.id)
        ], limit=1)
        if not gradebook_student_id:
            gradebook_student_id = app_gradebook_student_model.sudo().create({
                'admission_id': admission_id.id,
                'gradebook_id': course_id.gradebook_id.id or False
            })
        if not gradebook_subject_id:
            gradebook_subject_id = app_gradebook_subject_model.sudo().create({
                'admission_id': admission_id.id,
                'op_subject_id': op_subject_id.id,
                'gradebook_student_id': gradebook_student_id.id,
                'gradebook_id': op_subject_id.gradebook_id.id or False
            })
            
        return {'gradebook_student_id': gradebook_student_id, 'gradebook_subject_id': gradebook_subject_id}

