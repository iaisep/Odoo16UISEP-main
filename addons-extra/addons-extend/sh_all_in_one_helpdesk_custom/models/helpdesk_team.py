from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HelpdeskTeam(models.Model):
    _inherit = "helpdesk.team"

    def write(self, vals):
        res = super(HelpdeskTeam, self).write(vals)
        if vals.get('mail1') or vals.get('mail2') or vals.get('mail3'):
            alias_vals1 = self._alias_get_creation_values()
            alias_vals2 = self._alias_get_creation_values()
            alias_vals3 = self._alias_get_creation_values()
            vals.update({
                'alias_name1': alias_vals1.get('mail1', vals.get('mail1')),
                'alias_name2': alias_vals2.get('mail2', vals.get('mail2')),
            })
        return res
