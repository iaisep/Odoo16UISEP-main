# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ResCallSummary(models.Model):
    _name = 'res.call.summary'
    _description = 'ResCallSummary'

    partner_id = fields.Many2one('res.partner', string='Contacto lead', compute='_compute_partner_id')
    crm_lead_id = fields.Many2one('crm.lead', string='Crm Lead')
    summary = fields.Text('Resúmen')
    call_summary = fields.Text('Resúmen de la llamada')
    call_number = fields.Char('Número de llamada')


    @api.depends('crm_lead_id')
    def _compute_partner_id(self):
        for record in self:
            record.partner_id = record.crm_lead_id.partner_id if record.crm_lead_id else False
