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

    openeducat_parent_onboard_panel = fields.Selection(
        [('not_done', "Not done"), ('just_done', "Just done"),
         ('done', "Done"), ('closed', "Closed")],
        string="State of the parent onboarding layout step",
        default='not_done')
    core_onboarding_parent_layout_state = fields.Selection(
        [('not_done', "Not done"), ('just_done', "Just done"),
         ('done', "Done"), ('closed', "Closed")],
        string="State of the onboarding parent layout step",
        default='not_done')

    @api.model
    def action_close_parent_panel_onboarding(self):
        """ Mark the onboarding panel as closed. """
        self.env.user.company_id.openeducat_parent_onboard_panel = 'closed'

    # parent type layout start##

    @api.model
    def action_onboarding_parent_layout(self):
        """ Onboarding step for the quotation layout. """
        action = self.env.ref(
            'openeducat_parent_enterprise.'
            'action_onboarding_parent_layout').read()[0]
        return action

    def update_parent_onboarding_state(self):
        """ This method is called on the controller rendering method
            and ensures that the animations
            are displayed only one time. """
        steps = [
            'core_onboarding_parent_layout_state',
        ]
        return self._get_and_update_onboarding_state(
            'openeducat_parent_onboard_panel', steps)
