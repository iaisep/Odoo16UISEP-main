import logging

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)


class SurveyUser_input(models.Model):
    _inherit = 'survey.user_input'

    survey_type = fields.Selection(
        string='Tipo',
        selection=[('survey', 'Encuesta'), ('cert', 'Certificación'),('exam', 'Examen'),('assignment', 'Asignación')] ,  store=True, related="survey_id.survey_type"
    )
    channel_id = fields.Many2one('slide.channel', string='Asignatura', store=True, related="slide_id.channel_id") 

    channel_partner_id = fields.Many2one('slide.channel.partner', string="Alumno incrito, existente", store=True, compute="compute_slide_channel_partner")       
    
    admission_id = fields.Many2one('op.admission', string="Admission",  store=True, compute="compute_slide_channel_partner" )
    op_subject_id = fields.Many2one('op.subject', string="Asignatura", store=True, compute="compute_slide_channel_partner" )
    course_id = fields.Many2one('op.course', string="Curso",   store=True, compute="compute_slide_channel_partner")
    batch_id = fields.Many2one('op.batch', string="Grupo",   store=True, compute="compute_slide_channel_partner" )

    # Se suprime el comportamiento de eliminacion automatica dentro del desarrollo de una certificacion
    def _check_for_failed_attempt(self):
        return True

    @api.model
    def create(self, values):
        res = super(SurveyUser_input, self).create(values)    
        if res.survey_type in ('exam','assignment'):
            res.scoring_success = False        
        return res
    

    def write(self, values):
        try:
            if 'survey_type' in values and values['survey_type'] in ('exam', 'assignment'):
                values['scoring_success'] = False
            elif self.survey_type in ('exam', 'assignment'):
                values['scoring_success'] = False
        except Exception as e:
            _logger.error("************************** 'survey_type': %s", e)
        
        try:
            scoring_percentage = values.get('scoring_percentage', self.scoring_percentage)
            survey_id = self.survey_id if 'survey_id' not in values else self.env['survey.survey'].sudo().browse(values['survey_id'])
            if scoring_percentage >= survey_id.scoring_success_min and survey_id.scoring_type != 'no_scoring':
                slide_partner_id = values.get('slide_partner_id', self.slide_partner_id)
                if slide_partner_id:
                    slide_partner_id.completed = True
            elif survey_id.scoring_type == 'no_scoring':  
                slide_partner_id = values.get('slide_partner_id', self.slide_partner_id)
                if slide_partner_id:
                    slide_partner_id.completed = True
        except KeyError as e:
            _logger.error("************************** 'values': %s", e)
        except Exception as e:
            _logger.error("************************** 'slide_partner_id': %s", e)

        return super(SurveyUser_input, self).write(values)


        


    @api.depends('channel_id','partner_id')
    def compute_slide_channel_partner(self):
        channel_partner_id = False
        admission_id = False
        op_subject_id = False
        course_id = False
        batch_id = False
        search = False
        if self.channel_id and self.partner_id:
            search = self.env['slide.channel.partner'].search([('partner_id','=',self.partner_id.id),('channel_id','=',self.channel_id.id)], limit=1)
            if search:
                channel_partner_id = search
                admission_id = channel_partner_id.admission_id
                op_subject_id = channel_partner_id.op_subject_id
                course_id = channel_partner_id.course_id
                batch_id = channel_partner_id.batch_id
        self.channel_partner_id = channel_partner_id
        self.admission_id = admission_id
        self.op_subject_id = op_subject_id
        self.course_id = course_id
        self.batch_id = batch_id



