import logging
from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)



class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_academic_program = fields.Boolean(
        string='Producto académico',
    )
    
    course_type = fields.Selection(
        string='Modalidad',
        required=True,
        selection=[('none', 'Ninguno'),('online', 'Online'), ('classroom', 'Online y Classroom')] ,
        help="La modalidad cambia el comportamiento de un venta de venta al confirmase.\n\n"\
        "Ninguno: No realiza cambios a la venta, Odoo sigue su flujo nativo.\n"\
        "Online: Venta de un curso desde el portal o manualmente, no requiere proceso de admision.\n"\
        "Online y classroom: Venta de un curso desde el portal o manualmente, requiere proceso de admision y se llevan clases virtuales."
        )
    