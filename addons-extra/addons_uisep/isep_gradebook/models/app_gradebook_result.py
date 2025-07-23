
from datetime import datetime

from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import math
import logging

_logger = logging.getLogger(__name__)




class AppGradebookResult(models.Model):
    _name = 'app.gradebook.result'

    name = fields.Char('Nombre', compute="compute_name", store=True )
    description = fields.Char('Descripción', default="Evaluación" )
    
    survey_type = fields.Selection(
        string='Tipo',
        selection=[('assignment', 'Asignación'), ('exam', 'Examen'), ('interaction', 'Interacción'),('foro', 'Foro')]
    )

    channel_id = fields.Many2one('slide.channel', string='Asignatura', store=True)
    channel_partner_id = fields.Many2one('slide.channel.partner', string="Alumno inscrito, existente", store=True)       
    
    admission_id = fields.Many2one('op.admission', string="Admission",  store=True, related="gradebook_subject_id.admission_id" )
    partner_id = fields.Many2one('res.partner', string='Estudiante',  store=True,  related="admission_id.partner_id")
    op_subject_id = fields.Many2one('op.subject', string="Asignatura", store=True , related="gradebook_subject_id.op_subject_id" )
    course_id = fields.Many2one('op.course', string="Curso",   store=True,  related="admission_id.course_id" )
    batch_id = fields.Many2one('op.batch', string="Grupo",   store=True, related="admission_id.batch_id")

    scoring_total = fields.Float(string='Calificación')
    comment = fields.Text('Comentario')
    survey_user_input_id = fields.Many2one('survey.user_input', string="Evaluación",   store=True)
    gradebook_subject_id = fields.Many2one('app.gradebook.subject', string="Libreta - Dentro de asignatura",   store=True)
    rated_by = fields.Many2one('res.partner', string='Calificado por' )
    
    post_qty = fields.Integer(string='Cant. de Publicaciones')


    # No usen round, no funciona para 8.5
    def round_custom(self,num):
        if num - int(num) >= 0.5:
            return math.ceil(num)
        else:
            return math.floor(num)
    
    @api.model
    def create(self, values):
        res = super(AppGradebookResult, self).create(values)
        gradebook = res.gradebook_subject_id.gradebook_id or res.gradebook_subject_id.gradebook_student_id.gradebook_id        
        if gradebook:
            round_subject_result = gradebook.round_subject_result
            grading_scale = gradebook.grading_scale
            if round_subject_result:
                res.scoring_total = self.round_custom(res.scoring_total)
            if res.scoring_total > grading_scale:
                res.scoring_total = grading_scale
        return res
        
         
    def write(self, values):        
        gradebook = self.gradebook_subject_id.gradebook_id or self.gradebook_subject_id.gradebook_student_id.gradebook_id
        grading_scale = gradebook.grading_scale
        
        if gradebook and 'scoring_total' in values:
            round_subject_result = gradebook.round_subject_result
            scoring_total = values['scoring_total']

            if round_subject_result:
                scoring_total = self.round_custom(scoring_total)

            if scoring_total > grading_scale:
                scoring_total = grading_scale

            values['scoring_total'] = scoring_total
        
        return super(AppGradebookResult, self).write(values)

    
    @api.onchange('post_qty')
    def total_score_forum(self):        
        for rec in self:
            if rec.survey_type == 'foro':
                gradebook_id = rec.gradebook_subject_id.gradebook_id or rec.gradebook_subject_id.gradebook_student_id.gradebook_id
                forum_line = gradebook_id.gradebook_template_ids.filtered(lambda x: x.type == 'foro')
                if forum_line:
                    points = 10/forum_line[0].qty
                    scoring_total = points * rec.post_qty
                    if scoring_total > 10:
                        scoring_total = 10
                    rec.scoring_total = scoring_total
                
           

    @api.depends('op_subject_id','admission_id')
    def compute_name(self):
        for self in self:
            op_subject_id = 'N/A'
            application_number = 'N/A'
            if self.op_subject_id:
                op_subject_id = self.op_subject_id.name
            if self.admission_id:
                application_number = self.admission_id.application_number
            self.name  = "[ %s ] %s"% (application_number, op_subject_id)


    