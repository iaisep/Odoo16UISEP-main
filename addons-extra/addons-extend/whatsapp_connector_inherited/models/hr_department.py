from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError

class HrDepartment(models.Model):
    _inherit = "hr.department"

    is_coordinator = fields.Boolean(string="is_coordinator", default=False)

    @api.onchange('is_coordinator')
    def validate_unique_coordinator(self):
        '''validates that only one crm team is coordinator per company'''

        coordiantors = self.env['hr.department'].search([('company_id', '=', self.company_id.id),
                                                         ('is_coordinator', '=', True)])
        if len(coordiantors) > 0 and coordiantors.id != self.ids[0]:
            raise UserError(_("Ya existe un equipo de coordinadores: " + str(coordiantors.name)))