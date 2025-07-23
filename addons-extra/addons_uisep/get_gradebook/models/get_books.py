# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
import pytz
from datetime import datetime
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)

class AppGradebookStudent(models.Model):
    _inherit = 'app.gradebook.student'


    def action_get_books(self): 
        try:         

            # Encuestas
            result=self.env['survey.user_input'].search([                
                ('survey_type', 'in', ['exam','assignment']),
                ('state', '=', 'done'),
                ('test_entry', '=', False),
                ('send_to_book', '=', False)
            ])  
            _logger.info('result: %s', result)  
           
            for rs in result: 
                rs.send_result()                
        except Exception as e:
            _logger.error('ERROR AL TRATAR DE PASAR A LIBRETA: %s', str(e))

