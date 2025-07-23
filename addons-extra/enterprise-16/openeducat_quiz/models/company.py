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

    quiz_enterprise_onboard_panel = fields.Selection(
        [('not_done', "Not done"), ('just_done', "Just done"),
         ('done', "Done"), ('closed', "Closed")],
        string="State of the quiz onboarding step", default='not_done')
    onboarding_quiz_layout_state = fields.Selection(
        [('not_done', "Not done"), ('just_done', "Just done"),
         ('done', "Done"), ('closed', "Closed")],
        string="State of the onboarding quiz layout  step", default='not_done')
    onboarding_question_bank_layout_state = fields.Selection(
        [('not_done', "Not done"), ('just_done', "Just done"),
         ('done', "Done"), ('closed', "Closed")],
        string="State of the onboarding question bank layout  step",
        default='not_done')

    @api.model
    def action_close_quiz_panel_onboarding(self):
        """ Mark the onboarding panel as closed. """
        self.env.user.company_id.quiz_enterprise_onboard_panel = 'closed'

    # quiz layout starts##

    @api.model
    def action_onboarding_quiz_layout(self):
        """ Onboarding step for the quotation layout. """
        action = self.env.ref(
            'openeducat_quiz.action_onboarding_quiz_layout').read()[0]
        return action

    # question bank layout starts##

    @api.model
    def action_onboarding_question_bank_layout(self):
        """ Onboarding step for the quotation layout. """
        action = self.env.ref(
            'openeducat_quiz.action_onboarding_question_bank_layout').read()[0]
        return action

    def update_quiz_onboarding_state(self):
        """ This method is called on the controller rendering
            method and ensures that the animations
            are displayed only one time. """
        steps = [
            'onboarding_quiz_layout_state',
            'onboarding_question_bank_layout_state'
        ]
        return self._get_and_update_onboarding_state(
            'quiz_enterprise_onboard_panel', steps)
