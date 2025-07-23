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

    openeducat_exam_onboard_panel = fields.Selection(
        [('not_done', "Not done"),
         ('just_done', "Just done"),
         ('done', "Done"),
         ('closed', "Closed")],
        string="State of the onboarding exam layout step",
        default='not_done')
    onboarding_exam_type_layout_state = fields.Selection(
        [('not_done', "Not done"),
         ('just_done', "Just done"),
         ('done', "Done"),
         ('closed', "Closed")],
        string="State of the onboarding exam type layout step",
        default='not_done')
    onboarding_exam_room_layout_state = fields.Selection(
        [('not_done', "Not done"),
         ('just_done', "Just done"),
         ('done', "Done"),
         ('closed', "Closed")],
        string="State of the onboarding exam room layout step",
        default='not_done')
    onboarding_exam_grade_layout_state = fields.Selection(
        [('not_done', "Not done"),
         ('just_done', "Just done"),
         ('done', "Done"),
         ('closed', "Closed")],
        string="State of the onboarding exam grade layout step",
        default='not_done')

    @api.model
    def action_close_exam_panel_onboarding(self):
        """ Mark the onboarding panel as closed. """
        self.env.user.company_id.openeducat_exam_onboard_panel = 'closed'

    # exam type layout start##

    @api.model
    def action_onboarding_exam_layout(self):
        """ Onboarding step for the quotation layout. """
        action = self.env.ref('openeducat_exam_enterprise.'
                              'action_onboarding_exam_layout').read()[0]
        return action

    # exam room layout start##

    @api.model
    def action_onboarding_exam_room_layout(self):
        """ Onboarding step for the quotation layout. """
        action = self.env.ref('openeducat_exam_enterprise.'
                              'action_onboarding_exam_room_layout').read()[0]
        return action

    # exam grade layout start##

    @api.model
    def action_onboarding_exam_grade_layout(self):
        """ Onboarding step for the quotation layout. """
        action = self.env.ref('openeducat_exam_enterprise.'
                              'action_onboarding_exam_grade_layout').read()[0]
        return action

    def update_exam_onboarding_state(self):
        """ This method is called on the controller
         rendering method and ensures that the animations
            are displayed only one time. """
        steps = [
            'onboarding_exam_type_layout_state',
            'onboarding_exam_room_layout_state',
            'onboarding_exam_grade_layout_state'
        ]
        return self._get_and_update_onboarding_state(
            'openeducat_exam_onboard_panel', steps)
