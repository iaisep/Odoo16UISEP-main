
from datetime import datetime

from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)


class AppGradebookTemplateLine(models.Model):
    _name = 'app.gradebook.template.line'

    name = fields.Char("Nombre", compute="compute_name", store=True )
    type = fields.Selection(
        string='Tipo',
        selection=[('assignment', 'Asignaciones'), ('exam', 'Exámenes'), ('interaction', 'Interacciones'),('foro', 'Foro')], required=True
    )
    gradebook_id = fields.Many2one('app.gradebook', string='Calificaciones template' )
    weight = fields.Float(string='Peso %')
    qty = fields.Integer(string='Cantidad' )
    # points = fields.Float(string='Puntos por publicación' )


    @api.depends('type','weight','qty')
    def compute_name(self):
        for record in self:
            name = "Template"
            if record.type == "assignment":
                weight_formatted = '{:.2f}'.format(record.weight)
                name = "%s -> Peso %s %% -> Cant. %s" % ('Asignaciones',weight_formatted, str(record.qty))
            elif record.type == "exam":
                weight_formatted = '{:.2f}'.format(record.weight)
                name = "%s -> Peso %s %% -> Cant. %s" % ('Exámenes',weight_formatted, str(record.qty))
            elif record.type == "interaction":
                weight_formatted = '{:.2f}'.format(record.weight)
                name = "%s -> Peso %s %% -> Cant. %s" % ('Interacciones',weight_formatted, str(record.qty))
            elif record.type == "foro":
                weight_formatted = '{:.2f}'.format(record.weight)
                name = "%s -> Peso %s %% -> Cant. %s" % ('Foro',weight_formatted, str(record.qty))
                
            record.name = name
        
    

    @api.constrains('qty','weight','type')
    def _check_validation(self):
        for record in self:
            if record.qty <= 0 and record.type in ('assignment','exam','foro'):
                raise ValidationError('"Cantidad" debe ser mayor que cero.')
            
            # if record.points <= 0 and record.type in ('foro'):
            #    raise ValidationError('"Puntos por publicación" debe ser mayor que cero.')
            
            if record.weight <= 0:
                raise ValidationError('"Peso %" debe ser mayor que cero.')
            



    