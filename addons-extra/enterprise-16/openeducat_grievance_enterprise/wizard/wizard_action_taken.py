# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################


from odoo import fields, models


class WizardActionTaken(models.TransientModel):
    _name = "wizard.action.taken"
    _description = "Grievance Action Taken"

    action_taken = fields.Text("Action Taken")
    root_cause_id = fields.Many2one("grievance.root.cause", "Root Cause")

    def submit_action(self):
        context = dict(self.env.context)
        active_id = context.get('active_id')
        grievance_data = self.env['grievance'].browse(active_id)

        grievance_data.update({
            'action_taken': self.action_taken,
            'root_cause_id': self.env['grievance.root.cause'].browse(
                self.root_cause_id.id).id,
            'state': 'action'
        })
