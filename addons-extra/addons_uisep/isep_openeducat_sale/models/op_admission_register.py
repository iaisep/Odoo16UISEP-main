import logging
from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class OpAdmissionRegister(models.Model):
    _inherit = 'op.admission.register'    

    product_template_id = fields.Many2one('product.template', string="Plantilla de Producto", related="course_id.product_template_id" , store=True)

    period = fields.Char(
        string="Periodo",
        store=True,
    )

    @api.constrains('period','product_template_id')
    def _check_validations(self):
        for record in self:
            if record.period:
                if '-' not in record.period or len(record.period) != 7:
                    raise UserError("El periodo debe ser un formato valida, ejemplo: 2025-01")
            
            if record.period and record.product_template_id:
                if self.env['op.admission.register'].search_count([('period', '=', record.period), ('product_template_id', '=', record.product_template_id.id)]) > 1:
                    raise UserError("La combinación entre el periodo y el producto del curso debe ser única.")

