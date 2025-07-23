from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def action_send_student(self):
        result = super(SaleOrderLine, self).action_send_student()
        result['context']['default_birth_date'] = self.order_partner_id.birth_date
        return result
