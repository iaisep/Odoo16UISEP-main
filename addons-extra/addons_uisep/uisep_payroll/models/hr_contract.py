# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import time
import base64

import logging
logger = logging.getLogger(__name__)


class HrContract(models.Model):
    _inherit = "hr.contract"

    rule_third_ids = fields.Many2many('hr.contract.rule.third', string='Salary Rules With Third')


class HrContractRuleThird(models.Model):
    _name = 'hr.contract.rule.third'

    rule_id = fields.Many2one('hr.salary.rule', string='Salary Rule With Third', required=True, domain="[('partner_id', '!=', False)]")
    partner_id = fields.Many2one('res.partner', string='Partner', required=True, 
        help="Eventual third party involved in the salary payment of the employees.")
    company_id = fields.Many2one('res.company', required=True, index=True, default=lambda self: self.env.company)
    locked = fields.Boolean(string='Locked', required=True, help="Alert once blocked the user must not change the records...")
