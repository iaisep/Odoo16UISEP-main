from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError

class ProductTermSchedule(models.Model):
    _name = "product.term.schedule"
    _description = "Product term Schedule"

    name = fields.Char(string="Nro. Plazos Suscripción", required=True )
    term_number = fields.Integer('Nro. Plazos')
    custom = fields.Boolean(string="Es personalizado")

    
    @api.constrains('term_number')
    def _check_unique_admission_id(self):
        for record in self:
            if record.term_number <= 0:
                raise ValidationError('El número de meses no puede ser menor o igual a CERO.')
           
    