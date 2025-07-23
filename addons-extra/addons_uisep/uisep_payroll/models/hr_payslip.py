# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons import decimal_precision as dp
import time
import base64

import logging
logger = logging.getLogger(__name__)


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def action_payslip_done(self):
        res = super(HrPayslip, self).action_payslip_done()
        for slip in self:
            for mline in slip.move_id.line_ids:
                if not mline.partner_id:
                    mline.partner_id = slip.employee_id.address_home_id.id
            for sline in slip.line_ids:
                update = False
                partner = False
                for cr in sline.contract_id.rule_third_ids.filtered(lambda r: r.rule_id.id == sline.salary_rule_id.id and sline.partner_id.id == sline.salary_rule_id.partner_id.id and r.partner_id.id != sline.partner_id.id):
                    update = True
                    partner = cr.partner_id
                if sline.salary_rule_id.partner_id:
                    mlines = slip.move_id.line_ids.filtered(lambda x: x.partner_id.id == sline.partner_id.id and x.name == sline.name and x.debit > 0) if slip.move_id.line_ids else []
                    for ml in mlines:
                        if not update and ml.name == sline.name and ml.partner_id.id == sline.partner_id.id:
                            ml.partner_id = slip.employee_id.address_home_id.id

                    mlines = slip.move_id.line_ids.filtered(lambda x: x.partner_id.id == sline.partner_id.id and x.name == sline.name and x.credit > 0) if slip.move_id.line_ids else []
                    for ml in mlines:
                        if update and ml.name == sline.name and ml.partner_id.id == sline.partner_id.id:
                            ml.partner_id = partner.id

        return res


class HrSalaryRule(models.Model):
    _inherit = "hr.salary.rule"

    account_debit2_id = fields.Many2one('account.account', 'Debit Account Secondary', domain=[('deprecated', '=', False)])
    partner_debit = fields.Boolean('Employee Debit')
    partner_credit = fields.Boolean('Employee Credit')

