from odoo import models, fields, api,_
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    def action_assign_crm_crono(self):
        temamember=self.env['crm.team.member'].search([])
        for tem in temamember:
            self.crm_asig_lead(tem.user_id.id,1)
      

    def action_assign_crm(self):
        seller=self.env.user.id
        result=self.crm_asig_lead(seller,0)
        return result
    
    def crm_asig_lead(self,user,call):
        result=0
        equipment=self.env['crm.team.member'].sudo().search([('user_id','=',user)])
        _logger.info("EQUIPO %s",equipment)
        for it in equipment:            #
            leads_to_jobs=self.env['crm.lead'].sudo().search([('type','=','lead'),('team_id','=',it.crm_team_id.id),('user_id','=',1618),('stage_id.is_won','!=',True)])
            _logger.info("LEADS PARA ASIGNAR TRABAJAR %s",leads_to_jobs)
            jobs_leads=self.search_count([('type','=','lead'),('stage_id.is_won','!=',True),('user_id','=',user),('team_id','=',it.crm_team_id.id)])       
            _logger.info("LEADS EN TRABAJO %s",jobs_leads)            
            _logger.info(len(leads_to_jobs))          
            

            for lead in leads_to_jobs:
                if jobs_leads < it.assignment_max:
                    lead.user_id = user
                    _logger.info("LEAD ASIGNADO %s",lead.name)
                    result = 1                   
                    jobs_leads += 1
                else:                    
                   _logger.info("MAXIMO DE ASIGNACIONES %s",it.assignment_max)
                   result = 2
                    
        if call == 0:
            return result
       


