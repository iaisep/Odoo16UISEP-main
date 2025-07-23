from datetime import date, datetime
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

class ProductTemplate(models.Model):
    _inherit = "product.template"

    type_course=fields.Selection([('curso','Curso'),('mat','Matricula'),
    	('rec','Recargo'),('desc','Descuento'),('desc_ma','Descuento Matricula'),('diplo','Diplomado'),
    	('master','Matestria')],string="Tipo de curso")