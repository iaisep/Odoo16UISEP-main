import logging
from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class SlideChannelPartner(models.Model):
    _inherit = 'slide.channel.partner'

    course_id = fields.Many2one('op.course', string="Curso" )     
    batch_id = fields.Many2one('op.batch', string="Grupo" )
    register_id = fields.Many2one('op.admission.register', string="Registro de Admisión" )
    admission_id = fields.Many2one('op.admission', string="Admission" )
    op_subject_id = fields.Many2one('op.subject', string="ASIGNATURA" )
    active = fields.Boolean(string='Activo', default=True)
    
    date_to=fields.Date(string="Fecha de Fin", help="Fecha de Fin registrada en el Lote")
    date_from=fields.Date(string="Fecha de Inicio", help="Fecha de Inicio registrada en el Lote")