from odoo import models, fields
import logging
_logger = logging.getLogger(__name__)

class CRMAsignacion(models.TransientModel):
    _name = 'crm.asignacion'
    
    _description = 'Asignación de CRM'

    #relacion con crm
    crm_lead_ids = fields.Many2many('crm.lead', string='CRM')

    #relacion con res.users
    user_lead_id = fields.Many2one('res.users', string='Usuario')

    #relacion con crm.team
    team_lead_id = fields.Many2one('crm.team', string='Equipo')


    def action_asignacion(self):
        if self.user_lead_id:
            #recoremos el cada lead
            for lead in self.crm_lead_ids:
                lead.user_id = self.user_lead_id
               # _logger.info('action_asignacion %s', lead)
        if self.team_lead_id:
            for lead in self.crm_lead_ids:
                lead.team_id = self.team_lead_id
                #_logger.info('action_asignacion %s', lead)



