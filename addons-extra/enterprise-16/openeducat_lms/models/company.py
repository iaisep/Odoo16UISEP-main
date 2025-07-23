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

    lms_onboard_panel = fields.Selection(
        [('not_done', "Not done"),
         ('just_done', "Just done"),
         ('done', "Done"),
         ('closed', "Closed")],
        string="State of the lms onboarding step",
        default='not_done')
    onboarding_lms_course_layout_state = fields.Selection(
        [('not_done', "Not done"),
         ('just_done', "Just done"),
         ('done', "Done"),
         ('closed', "Closed")],
        string="State of the onboarding lms course layout step",
        default='not_done')
    onboarding_material_layout_state = fields.Selection(
        [('not_done', "Not done"),
         ('just_done', "Just done"),
         ('done', "Done"),
         ('closed', "Closed")],
        string="State of the onboarding material layout step",
        default='not_done')
    onboarding_enrollment_layout_state = fields.Selection(
        [('not_done', "Not done"),
         ('just_done', "Just done"),
         ('done', "Done"),
         ('closed', "Closed")],
        string="State of the onboarding enrollment layout step",
        default='not_done')
    onboarding_course_category_layout_state = fields.Selection(
        [('not_done', "Not done"),
         ('just_done', "Just done"),
         ('done', "Done"),
         ('closed', "Closed")],
        string="State of the onboarding course category layout step",
        default='not_done')

    @api.model
    def action_close_lms_onboarding(self):
        """ Mark the onboarding panel as closed. """
        self.env.user.company_id.lms_onboard_panel = 'closed'

    # course layout starts

    @api.model
    def action_lms_onboarding_course_layout(self):
        """ Onboarding step for the quotation layout. """
        action = self.env.ref(
            'openeducat_lms.action_lms_onboarding_course_layout').read()[0]
        return action

    # material layout starts

    @api.model
    def action_onboarding_material_layout(self):
        """ Onboarding step for the quotation layout. """
        action = self.env.ref(
            'openeducat_lms.action_onboarding_material_layout').read()[0]
        return action

    # enrollment layout starts

    @api.model
    def action_onboarding_enrollment_layout(self):
        """ Onboarding step for the quotation layout. """
        action = self.env.ref(
            'openeducat_lms.action_onboarding_enrollment_layout').read()[0]
        return action

    # course category layout starts

    @api.model
    def action_onboarding_course_category_layout(self):
        """ Onboarding step for the quotation layout. """
        action = self.env.ref(
            'openeducat_lms.'
            'action_onboarding_course_category_layout').read()[0]
        return action

    def update_lms_onboarding_state(self):
        """ This method is called on the controller rendering
         method and ensures that the animations
            are displayed only one time. """
        steps = [
            'onboarding_lms_course_layout_state',
            'onboarding_material_layout_state',
            'onboarding_enrollment_layout_state',
            'onboarding_course_category_layout_state'
        ]
        return self._get_and_update_onboarding_state(
            'lms_onboard_panel', steps)
