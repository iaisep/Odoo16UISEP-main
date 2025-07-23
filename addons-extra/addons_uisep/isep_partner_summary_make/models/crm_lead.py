# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    summary_ids=fields.One2many(
        'res.call.summary',
        'crm_lead_id',string="Resúmen de llamadas")
    next_action_date = fields.Datetime(string="Proxima fecha de acción")

    manage_reason = fields.Selection([
            ('1', 'No localizado'),
            ('2', 'Localizado'),
            ('3', 'En Gestión'),
            ('4', 'Llamar luego'),
            ('5', 'No molestar')
        ], string='Motivo de Gestión')


    action_request_lead = fields.Selection([
            ('1', 'WhatsApp'),
            ('2', 'Llamada con asesor'),
            ('3', 'Envío de documento a firmar'),
            ('4', 'Enviar el presupuesto')
        ], string='Acción solicitada por lead')


    last_action_date = fields.Datetime(
        string="Fecha de última acción")
    
    gestion_mo = fields.Selection(
        [('1', 'Buzon'),
         ('2', 'Numero incorrecto'),
         ('3', 'Numero invalido'),
         ('4', 'Lead molesto'),
         ('5', 'No localizado')],
        string="Gestión MO", default='1')

    gr_source = fields.Char('Origen')
    gr_campaingn = fields.Char('Campaña')
    gr_term = fields.Char('Term')
    gr_gadid = fields.Char('ID Gads')
    gr_content = fields.Char('Contenido')


    def write(self, vals):
        res = super(CrmLead, self).write(vals)
        stage_dest = self.env['crm.stage'].search([('is_final', '=', True)], limit=1)
        empty_summaries = len(self.summary_ids.filtered(lambda s: not s.call_summary))
        empty_records = self.summary_ids.filtered(lambda s: not s.call_summary)
        for lead in self:            
            if lead.active and lead.stage_id.is_initial and empty_summaries >= 5:
                lead.stage_id = stage_dest.id
                empty_records.with_context(avoid_recursion=True).write({
                'call_summary': 'sin contacto'
                })
            if lead.active and lead.stage_id.is_final and empty_summaries >= 25:
                self.action_archive()
                empty_records.with_context(avoid_recursion=True).write({
                'call_summary': 'perdido'
                })
        return res

class CrmStage(models.Model):
    _inherit = 'crm.stage'

    is_final = fields.Boolean(string="Es Destino", default=False)
    is_initial = fields.Boolean(string="Es inicial", default=False)
