from odoo import models, fields, api,_
import logging
_logger = logging.getLogger(__name__)

class CustomTypeForm(models.Model):

    _inherit = 'mk.typeform.model.relation'  

    type_field=fields.Selection(
        selection_add=[("condition", "Codicional")],
        ondelete={'condition': 'cascade'}
    )
  
    conditon_id=fields.One2many('mk.typeform.fields.condition','codition_type_form_id',string="Reglas de Condición")

      
 
class CustomFieldsCondition(models.Model):

    _name='mk.typeform.fields.condition'
    _description='Fields Condition'

    key_value_one = fields.Char(string="Key Value One")

    key_value_two = fields.Char(string="Key Value Two")

    value_one=fields.Char(string="Value One")

    value_two=fields.Char(string="Value Two")

    result=fields.Char(string="Result ID")

    codition_type_form_id=fields.Many2one('mk.typeform.model.relation',string="Type Form")

