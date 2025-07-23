# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    openeducat_assignment_onboard_panel = fields.Selection(
        [('not_done', "Not done"),
         ('just_done', "Just done"),
         ('done', "Done"),
         ('closed', "Closed")],
        string="State of the onboarding assignment layout step",
        default='not_done')
    onboarding_assignment_type_layout_state = fields.Selection(
        [('not_done', "Not done"),
         ('just_done', "Just done"),
         ('done', "Done"),
         ('closed', "Closed")],
        string="State of the onboarding assignment type layout step",
        default='not_done')

    @api.model
    def action_close_assignment_panel_onboarding(self):
        """ Mark the onboarding panel as closed. """
        self.env.user.company_id.openeducat_assignment_onboard_panel = 'closed'

    # assignment type layout start##

    @api.model
    def action_onboarding_assignment_type_layout(self):
        """ Onboarding step for the quotation layout. """
        action = self.env.ref(
            'openeducat_assignment_enterprise.'
            'action_onboarding_assignment_type_layout').read()[0]
        return action

    def update_assignment_onboarding_state(self):
        """ This method is called on the controller
         rendering method and ensures that the animations
            are displayed only one time. """
        steps = [
            'onboarding_assignment_type_layout_state',
        ]
        return self._get_and_update_onboarding_state(
            'openeducat_assignment_onboard_panel', steps)
