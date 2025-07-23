from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class HrPayslipEdi(models.Model):
    _inherit = "hr.payslip.edi"

    def compute_sheet(self):
        for rec in self:
            if rec.papayslip_ids:
                for payslip in rec.papayslip_ids:
                    if payslip.company_id.country_id.code == 'CO':
                        res = super(HrPayslipEdi, self).compute_sheet()
        return res
