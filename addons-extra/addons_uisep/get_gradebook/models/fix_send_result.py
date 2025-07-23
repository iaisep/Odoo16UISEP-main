# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
import pytz
from datetime import datetime
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)

class FixSurveyUser_input(models.Model):
    
    _inherit = 'survey.user_input'

    send_to_book = fields.Boolean(string='Enviadio a Libreta', default=False)

    def write(self, vals):
        res = super(FixSurveyUser_input, self).write(vals)
        if 'comment' in vals:
            self.result_id.comment = vals['comment']
        return res
    
    def valite_send_result(self):
        temp = self.env['op.subject'].search([
                        ('slide_channel_id', '=', self.channel_id.id)
                    ],limit=1) 
        if temp:
            self.op_subject_id = temp.id
            self.gradebook_subject_id = temp.id
        if self.survey_type in ['assignment']:
            self.scoring_percentage=self.answer_score_total    

    def send_result(self):
        rated_by = self.env.user.partner_id.id or False
        

        
        if self.admission_id and self.op_subject_id:
            # answer_score_total = 0
            
            # if self.user_input_line_ids:
            #     answer_score_total=sum(self.user_input_line_ids.mapped('answer_score'))
            self.valite_send_result()            
            if self.scoring_percentage==0.0:
                pass
            else:

                result_id = self.result_id            
                if not self.result_id:                
                    self.search_subject()
                    course_id = 'N/A'
                    application_number = 'N/A'
                    description = "Evaluación"
                    if self.course_id:
                        course_id = self.course_id.name
                    if self.admission_id:
                        application_number = self.admission_id.application_number
                    description  = "%s - %s"% (application_number, course_id)                
                    data = {
                        'name': self.survey_id.title,
                        'survey_user_input_id': self.id,
                        'channel_id': self.channel_id.id,
                        'channel_partner_id': self.channel_partner_id.id,                  
                        'scoring_total': self.scoring_percentage,
                        'gradebook_subject_id': self.gradebook_subject_id.id,
                        'survey_type': self.survey_type,
                        'description': description,                       
                        'rated_by': rated_by
                    }                      
                    

                    result_id = self.env['app.gradebook.result'].create(data)
                    self.send_to_book = True

                  
                self.result_id = result_id
                self.rated_by = rated_by


