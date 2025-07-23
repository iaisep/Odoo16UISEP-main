# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    certificado_web = fields.Boolean(
        string="Certificado Web",
    )

    def get_last_payment_date(self):
        self.ensure_one()  # Ensure this method is called on a single record
        if self.invoice_payments_widget and 'content' in self.invoice_payments_widget.keys():
            filtered_data = [item for item in self.invoice_payments_widget['content'] if item['amount'] > 0]
            if len(filtered_data) > 0 :
                data_sorted = sorted(filtered_data, key=lambda x: x['date'], reverse=True)
                last_payment_date = data_sorted[0]['date']
                return last_payment_date 
        return None

