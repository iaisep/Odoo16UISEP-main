import logging
from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class OpAssignmentSubLine(models.Model):
    _inherit = 'op.assignment.sub.line'


    def open_reg(self):
        self.ensure_one()
        action = {
            'name': 'Presentacion',
            'type': 'ir.actions.act_window',
            'res_model': 'op.assignment.sub.line', 
            'view_mode': 'form',
            'view_id': self.env.ref('openeducat_assignment.view_op_assignment_sub_line_form').id, 
            'target': 'current',
            'res_id': self.id
        }
        return action
