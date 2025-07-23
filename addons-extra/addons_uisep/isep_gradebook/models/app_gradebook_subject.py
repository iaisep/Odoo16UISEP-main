
from datetime import datetime

from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import math
import logging

_logger = logging.getLogger(__name__)


class AppGradebookSubject(models.Model):
    _name = 'app.gradebook.subject'

    name = fields.Char(string='Asignatura', store=True, compute="compute_name")
    
    gradebook_student_id = fields.Many2one('app.gradebook.student', string="gradebook student",  ondelete="cascade" )
    gradebook_result_ids = fields.One2many('app.gradebook.result', 'gradebook_subject_id', string="Asignaturas" )
    admission_id = fields.Many2one('op.admission', string="Admission",  store=True, related="gradebook_student_id.admission_id")
    partner_id = fields.Many2one('res.partner', string='Contacto', related="gradebook_student_id.partner_id", store=True)
    gradebook_id = fields.Many2one('app.gradebook', string='Calificaciones template', store=True, compute="compute_gradebook_id" )
    course_id = fields.Many2one('op.course',  related="gradebook_student_id.course_id", string="Curso",   store=True)
    op_subject_id = fields.Many2one('op.subject', string="Asignatura" , domain="[('course_id','=', course_id)]" )

    # Se debe crear los fields float necesarios para cada tipo de promedio
    # ('assignment', 'Asignaciones'), ('exam', 'Exámenes'), ('interaction', 'Interacciones'),('foro', 'Foro')    
    point_average_assignment = fields.Float(string='AVG Asignaciones' , compute="compute_point_average" , store=True)
    point_average_exam = fields.Float(string='AVG Exámenes' , compute="compute_point_average" , store=True)
    point_average_interaction = fields.Float(string='AVG Interacciones' , compute="compute_point_average" , store=True)
    point_average_foro = fields.Float(string='AVG Foro' , compute="compute_point_average" , store=True)


    info_assignment = fields.Char(string='Info Asignaciones' , compute="compute_point_average" , store=True)
    info_exam = fields.Char(string='Info Exámenes' , compute="compute_point_average" , store=True)
    info_interaction = fields.Char(string='Info Interacciones' , compute="compute_point_average" , store=True)
    info_foro = fields.Char(string='Info Foro' , compute="compute_point_average" , store=True)

    show_assignment = fields.Boolean(string='Visible Asignaciones' , compute="compute_data_show" , store=True)
    show_exam = fields.Boolean(string='Visible Exámenes' , compute="compute_data_show" , store=True)
    show_interaction = fields.Boolean(string='Visible Interacciones' , compute="compute_data_show" , store=True)
    show_foro = fields.Boolean(string='Visible Foro' , compute="compute_data_show" , store=True)

    final_subject_note = fields.Float(string='Calificación final' , compute="compute_final_subject_note" , store=True)
    state = fields.Selection(
        string='Estado',
        selection=[('draft', 'Borrador'),('in_progress', 'En proceso'), ('done', 'Finalizado') ], compute="compute_state", store=True
    )

    def unlink_subject(self):
        for rec in self:
            rec.unlink()
    

    def round_custom(self,num):
        if num - int(num) >= 0.5:
            return math.ceil(num)
        else:
            return math.floor(num)


    @api.constrains('gradebook_result_ids')
    def _check_validation(self):
        for record in self:            
            foro = record.gradebook_result_ids.filtered( lambda x: x.survey_type == 'foro' )
            if len(foro) > 1:
                raise ValidationError('No puede ingresar el Tipo "Foro" más de 1 vez.')
            
            interaction = record.gradebook_result_ids.filtered( lambda x: x.survey_type == 'interaction' )
            if len(interaction) > 1:
                raise ValidationError('No puede ingresar el Tipo "Interacción" más de 1 vez.')



    @api.depends('gradebook_student_id.state')
    def compute_state(self):
        for rec in self:
            rec.state=rec.gradebook_student_id.state


    @api.depends('point_average_assignment','point_average_exam','point_average_interaction','point_average_foro')
    def compute_final_subject_note(self):
        for rec in self:
            gradebook = rec._get_gradebook_info(rec)
            # Atento, existe una validacion en Gradebook (app.gradebook) que obliga a que la sumatoria de pesos sea igual al 100%
            # vamos a obtener las reglas de los pesos de la variable gradebook teniendo garantizado que la suma de pesos es 100
            assignment = exam = interaction = foro = 0
            final_subject_note = 0

            if gradebook['assignment']['weight']:
                final_subject_note += rec.point_average_assignment * (gradebook['assignment']['weight']/100)

            if gradebook['exam']['weight']:
                final_subject_note += rec.point_average_exam * (gradebook['exam']['weight']/100)
            
            if gradebook['interaction']['weight']:
                final_subject_note += rec.point_average_interaction * (gradebook['interaction']['weight']/100)
            
            if gradebook['foro']['weight']:
                final_subject_note += rec.point_average_foro * (gradebook['foro']['weight']/100)

            # rec.final_subject_note = final_subject_note

            gradebook_id = rec.gradebook_id or rec.gradebook_student_id.gradebook_id
            round_subject_final = gradebook_id.round_subject_final
            if gradebook_id and round_subject_final:
                final_subject_note = self.round_custom(final_subject_note)          
            
            rec.final_subject_note = final_subject_note
            


    @api.depends('gradebook_id','gradebook_id.gradebook_template_ids','gradebook_student_id.gradebook_id', 'gradebook_student_id.gradebook_id.gradebook_template_ids')
    def compute_data_show(self):
        for rec in self:
            show_assignment = False
            show_exam = False
            show_interaction = False
            show_foro = False
            gradebook_id = rec.gradebook_id or rec.gradebook_student_id.gradebook_id
            for line in gradebook_id.gradebook_template_ids:
                if line.type == 'assignment':
                    show_assignment = True
                elif line.type == 'exam':
                    show_exam = True
                elif line.type == 'interaction':
                    show_interaction = True
                elif line.type == 'foro':
                    show_foro = True
            
            rec.show_assignment = show_assignment
            rec.show_exam = show_exam
            rec.show_interaction = show_interaction
            rec.show_foro = show_foro
    


    def _get_gradebook_info(self, rec):
        # Vamos a definir el dict de una vez con su estructura:
        gradebook = {
            'assignment': {
                'weight': False,
                'qty': False,
            },
            'exam': {
                'weight': False,
                'qty': False,
            },
            'interaction': {
                'weight': False,
                'qty': False,
            },
            'foro': {
                'weight': False,
                'qty': False,
            }
        }
        gradebook_id = rec.gradebook_id or rec.gradebook_student_id.gradebook_id
        for gb in gradebook_id.gradebook_template_ids:
            # Tenemos una validacion que solo permite 1 de cada tipo, asi que podemos con un if.
            if gb.type == 'assignment':
                gradebook['assignment']['weight'] = gb.weight
                gradebook['assignment']['qty'] = gb.qty
            if gb.type == 'exam':
                gradebook['exam']['weight'] = gb.weight
                gradebook['exam']['qty'] = gb.qty            
            if gb.type == 'foro':
                gradebook['foro']['weight'] = gb.weight
                gradebook['foro']['qty'] = gb.qty 
            if gb.type == 'interaction':
                gradebook['interaction']['weight'] = gb.weight
                gradebook['interaction']['qty'] = 1 # siempre sera 1
                # su nota se obtiene desde elearning % de avance
                      
        return gradebook

    @api.depends('gradebook_result_ids.scoring_total','gradebook_id','gradebook_student_id.gradebook_id')
    def compute_point_average(self):
        for rec in self:
            assignment_total = 0            
            assignment_count = 0

            exam_total = 0
            exam_count = 0

            interaction_total = 0
            interaction_count = 0

            foro_total = 0
            foro_count = 0


            info_assignment = "No definido"
            info_exam = "No definido"
            info_interaction = "No definido"
            info_foro = "No definido"

            point_average_assignment = point_average_exam = point_average_interaction = point_average_foro = 0

            if rec.gradebook_id or rec.gradebook_student_id.gradebook_id:
                gradebook = self._get_gradebook_info(rec)

                for result in rec.gradebook_result_ids:
                    if result.survey_type == 'assignment':
                        assignment_total += result.scoring_total
                        assignment_count += 1
                    elif result.survey_type == 'exam':
                        exam_total += result.scoring_total
                        exam_count += 1
                    elif result.survey_type == 'interaction':
                        interaction_total += result.scoring_total
                        interaction_count += 1
                    elif result.survey_type == 'foro':
                        foro_total += result.scoring_total
                        foro_count += 1
                
                if gradebook['assignment']['qty'] and gradebook['assignment']['weight']:                
                    info_assignment = '[ %s de %s ] Peso: %s %%' % ( str(assignment_count) , str(gradebook['assignment']['qty']) , str(gradebook['assignment']['weight'])  )

                if gradebook['exam']['qty'] and gradebook['exam']['weight']:                
                    info_exam = '[ %s de %s ] Peso: %s %%' % ( str(exam_count) , str(gradebook['exam']['qty']) , str(gradebook['exam']['weight'])  )

                if gradebook['interaction']['qty'] and gradebook['interaction']['weight']:                
                    info_interaction = 'Peso: %s %%' % ( str(gradebook['interaction']['weight'])  )
                    # info_interaction = '[ %s de %s ] Peso: %s %%' % ( str(interaction_count) , str(gradebook['interaction']['qty']) , str(gradebook['interaction']['weight'])  )
                
                if gradebook['foro']['qty'] and gradebook['foro']['weight']:                
                    # info_foro = '[ %s de %s ] Peso: %s %%' % ( str(foro_count) , str(gradebook['foro']['qty']) , str(gradebook['foro']['weight'])  )
                    info_foro = '[ Req. pub. %s ] Peso: %s %%' % ( str(gradebook['foro']['qty']) , str(gradebook['foro']['weight'])  )

                point_average_assignment = (assignment_total / assignment_count) if gradebook['assignment']['qty'] == assignment_count and assignment_count > 0 else 0
                point_average_exam = (exam_total / exam_count) if gradebook['exam']['qty'] == exam_count and exam_count > 0 else 0
                point_average_interaction = interaction_total / interaction_count if 1 == interaction_count and interaction_count > 0  else 0  # gradebook['interaction']['qty']
                point_average_foro = foro_total / foro_count if 1 ==  foro_count and foro_count > 0 else 0 # gradebook['foro']['qty']

                rec.info_assignment = info_assignment
                rec.info_exam = info_exam
                rec.info_interaction = info_interaction
                rec.info_foro = info_foro

            # Calcula los promedios
            gradebook_id = rec.gradebook_id or rec.gradebook_student_id.gradebook_id
            round_subject_avg = gradebook_id.round_subject_avg
            if gradebook_id and round_subject_avg:
                point_average_assignment = self.round_custom(point_average_assignment)
                point_average_exam = self.round_custom(point_average_exam)
                point_average_interaction = self.round_custom(point_average_interaction)
                point_average_foro = self.round_custom(point_average_foro)            
            
            rec.point_average_assignment = point_average_assignment
            rec.point_average_exam = point_average_exam
            rec.point_average_interaction = point_average_interaction
            rec.point_average_foro = point_average_foro


    @api.depends('op_subject_id', 'admission_id')
    def compute_gradebook_id(self):
        for rec in self:
            if rec.op_subject_id:
                rec.gradebook_id = rec.op_subject_id.gradebook_id
            else:
                rec.gradebook_id = False

    @api.depends('op_subject_id','admission_id')
    def compute_name(self):
        for self in self:
            op_subject_id = 'N/A'
            application_number = 'N/A'
            if self.op_subject_id:
                op_subject_id = self.op_subject_id.name
            if self.admission_id:
                application_number = self.admission_id.application_number
            self.name  = "%s - %s"% (application_number, op_subject_id)
    
