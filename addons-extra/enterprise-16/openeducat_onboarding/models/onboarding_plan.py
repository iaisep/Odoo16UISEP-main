from odoo import fields, models


class OnboardingPlan(models.Model):
    _name = 'oe.onboarding.plan'
    _description = 'Onboarding Plan'

    name = fields.Char(string="Plan Name")
    step_id = fields.One2many('oe.onboarding.steps', 'plan_id', string='Steps')
