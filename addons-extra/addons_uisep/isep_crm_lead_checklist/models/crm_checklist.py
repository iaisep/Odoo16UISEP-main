from odoo import fields, models, api, _
import dateutil
import pytz
from datetime import datetime

class CrmChecklist(models.Model):
    _name = 'crm.checklist'
    
    
    name = fields.Char(string="Checklist" , related="checklist_id.name", required=True)
    checklist_id = fields.Many2one(comodel_name='crm.checklist.line', string="Checklist" , required=True)
    note = fields.Html(string='Notas', required=True)
    lead_id = fields.Many2one(comodel_name='crm.lead' , ondelete="cascade")

    user_id = fields.Many2one('res.users', store=True , string="Asesor" , related="lead_id.user_id")

    team_id = fields.Many2one('crm.team', store=True , string="Equipo" , related="lead_id.team_id")
    date = fields.Date('Fecha', store=True )    
    

    type = fields.Selection(
        string='Tipo',
        selection=[('lead', 'Lead'), ('opportunity', 'Oportunidad')],
        related="lead_id.type"
    )


    @api.onchange('note')
    def _onchange_checklist_id(self):
        if self.team_id:
            return {'domain': {'checklist_id': [('team_ids', 'in', [self.team_id.id])]}}
        else:
            return {'domain': {'checklist_id': []}}
    
    @api.model
    def default_get(self, fields):
        res = super(CrmChecklist, self).default_get(fields)
        user_tz = pytz.timezone(self.env.user.tz
                                or self.env.user.company_id.resource_calendar_id.tz
                                or 'UTC')
        date=pytz.utc.localize(datetime.now()).astimezone(user_tz).date()
        res['date'] = date
        
    
        return res
      

class CrmChecklistLine(models.Model):
    _name = 'crm.checklist.line'
    _order="sequence asc"

    name = fields.Char(string='Procedimiento', help='Descripcion de la actividad a realizar' , required=True)
    qty = fields.Integer('Cantidad', default=1)
    evaluar = fields.Boolean('Suma al porcentaje?', default=True)
    sequence = fields.Integer('Secuencia')
    active = fields.Boolean(string="Activo" ,default=True)
    team_ids = fields.Many2many('crm.team', string='Equipo de ventas', required=True)
    type = fields.Selection(
        string='Tipo',
        selection=[('lead', 'Lead'), ('opportunity', 'Oportunidad')],
        required=True
    )

    

    def name_get(self):
        self.browse(self.ids).read(['name', 'qty'])
        return [(template.id, '%s%s' % (template.qty and '[x%s] ' % str(template.qty).zfill(2) or '', template.name)) for template in self]
    
    
    