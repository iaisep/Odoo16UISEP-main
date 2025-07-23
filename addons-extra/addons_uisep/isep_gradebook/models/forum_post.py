# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
import logging

_logger = logging.getLogger(__name__)


class Post(models.Model):
    _inherit = 'forum.post'

    # FORO 
    @api.model_create_multi
    def create(self, vals_list):
        posts = super(Post, self.with_context(mail_create_nolog=True)).create(vals_list)
        
        for post in posts:
            channel_id = post.sudo().forum_id.slide_channel_id
            partner_id = post.sudo().create_uid.partner_id

            channel_partner_id = False
            admission_id = False
            op_subject_id = False
            course_id = False
            gradebook_subject = False
            # _logger.info('######### 01 #########################')
            if channel_id:
                channel_partner_id = post.env['slide.channel.partner'].sudo().search([('partner_id','=',partner_id.id),('channel_id','=',channel_id.id)], limit=1)
                admission_id = channel_partner_id.sudo().admission_id
                op_subject_id = channel_partner_id.sudo().op_subject_id
                course_id = channel_partner_id.sudo().course_id

                # search_gradebook_subject(partner_id,admission_id,course_id,op_subject_id):
                if admission_id and op_subject_id and course_id and op_subject_id.subject_type == "compulsory":
                    gradebook_subject = channel_partner_id.sudo().search_gradebook_subject(partner_id,admission_id,course_id,op_subject_id)
                    # gradebook_subject devuelve {'gradebook_student_id': gradebook_student_id, 'gradebook_subject_id': gradebook_subject_id}

                    gradebook_result_foro = gradebook_subject['gradebook_subject_id'].sudo().gradebook_result_ids.filtered(lambda d: d.survey_type == 'foro')
                    
                    # ANTES DE CREAR O ACTUALIZAR  DEBEMOS EVALUAR SI EXISTE FORO EN EL TEMPLATE DE GRADEBOOK
                    gradebook = gradebook_subject['gradebook_subject_id'].gradebook_id or gradebook_subject['gradebook_student_id'].gradebook_id
                    if 'foro' in gradebook.gradebook_template_ids.mapped('type'):
                        if not gradebook_result_foro:
                            application_number = admission_id.sudo().application_number
                            description = "%s - Foro: %s" % (application_number, course_id.name)
                            data = {
                                'name': description,
                                'channel_id': channel_id.id,
                                'channel_partner_id': channel_partner_id.id,
                                'post_qty': 1,
                                'gradebook_subject_id': gradebook_subject['gradebook_subject_id'].id,
                                'survey_type': 'foro',
                                'description': description,
                            }
                            result = post.env['app.gradebook.result'].sudo().create(data)
                            result.sudo().total_score_forum()
                        else:
                            gradebook_result_foro[0].post_qty = gradebook_result_foro[0].post_qty + 1
                            gradebook_result_foro[0].sudo().total_score_forum()
                
        return posts

    
    