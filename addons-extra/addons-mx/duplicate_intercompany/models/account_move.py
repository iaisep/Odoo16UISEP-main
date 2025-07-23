from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = "account.move"

    def cambiar_factura_de_compania(self):
        account_move = self.id
        return {
                'name': _('Cambiar factura de compania'),
                'type': 'ir.actions.act_window',
                "view_type": "form",
                'view_mode': 'form',
                'res_model': 'cambiar.factura.de.compania',
                'target': 'new',
                'context': {'default_account_move': account_move}
            }





