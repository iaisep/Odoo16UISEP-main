from odoo import models, fields, api
import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)

class OpCourseOP(models.Model):

    _inherit = 'op.course'

    official_title = fields.Boolean(string='Titulo oficial')
    
    @api.onchange('official_title')
    def activate_official_title(self):
        usuers_student=self.env['op.admission.register'].search([('course_id','=',self._origin.id)]) 
        if not usuers_student:
            for record in self.search([]):
                usuers_student=self.env['op.admission.register'].search([('course_id','=',record.id)])
                _logger.info("DATAS uno%s",usuers_student)
                for user in usuers_student.admission_ids:
                    _logger.info("OPCION %s",self)
                    user.partner_id.official_title = record.official_title
        else:             
            for user in usuers_student.admission_ids:
                user.partner_id.official_title = self.official_title    
     