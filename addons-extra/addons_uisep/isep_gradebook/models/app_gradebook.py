
from datetime import datetime

from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

import logging

_logger = logging.getLogger(__name__)



class AppGradebook(models.Model):
    _name = 'app.gradebook'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Plantilla')
    total_percent = fields.Float(string='Porcentaje total' , compute="compute_total_percent", store=True )
    gradebook_template_ids = fields.One2many('app.gradebook.template.line', 'gradebook_id',  string='Calificaciones template', tracking=True )
    
    round_subject_result = fields.Boolean('Detalle de asignatura, redondear a entero')
    round_subject_avg = fields.Boolean('Promedio de asignatura, redondear a entero')
    round_subject_final = fields.Boolean('Nota final de asignatura, redondear a entero')


    grading_scale = fields.Float('Escala de calificaciones', default=10 )


    content_pdf_top = fields.Html(string="Parte superior")
    content_pdf_bottom = fields.Html(string="Parte Inferior")


        

    @api.constrains('total_percent','grading_scale')
    def _check_validation(self):
        for record in self:
            if round(record.total_percent,2) != 100:
                raise ValidationError('"Porcentaje total" debe ser igual a 100%.')

            if record.grading_scale < 1:
                raise ValidationError('"Escala de calificaciones" debe ser mayor que Cero.')     

            if not record.gradebook_template_ids:
                raise ValidationError('Debe ingresar lineas a la plantilla.')
            
            types = []
            for line in record.gradebook_template_ids:
                types.append(line.type)
            if len(types) != len(set(types)):
                raise ValidationError('No puede ingresar el mismo "Tipo" más de 1 vez.')


    
    @api.depends('gradebook_template_ids.weight','gradebook_template_ids')
    def compute_total_percent(self):
        for record in self:
            total_percent = 0
            if record.gradebook_template_ids:
                total_percent = sum(self.gradebook_template_ids.mapped('weight'))
            record.total_percent = total_percent
        
    