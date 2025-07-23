import logging
from odoo.exceptions import ValidationError, UserError
from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class SurveySurvey(models.Model):
    _inherit = 'survey.survey'

   

    """@api.model
    def create(self, values):
        
        result = super().create(values)
        for line in self.slide_channel_ids:
            for cur in line.op_subject_ids:                
                if cur.course_id.gradebook_id:
                    raise UserError('Se requiere establecer una rubrica para las calificaciones, diríjase a la curso de %s y establezca uno. ' % (cur.course_id.name))

        
        return result"""