from odoo import api, fields, models


class OnboardingSteps(models.Model):
    _name = 'oe.onboarding.steps'
    _description = 'Onboarding Steps'

    name = fields.Char(string="Sequence", readonly=1)
    step_name = fields.Char(string="Steps Name")
    action_id = fields.Many2one('ir.actions.act_window', string='Action')
    plan_id = fields.Many2one('oe.onboarding.plan', string='Plan')
    is_done = fields.Boolean(string="Done ?")
    image = fields.Binary()
    is_start = fields.Boolean()
    doc_link = fields.Text()
    youtube_link = fields.Text()

    @api.model
    def create(self, vals):
        if not vals.get('name'):
            seq = self.env['ir.sequence'].next_by_code('oe.onboarding.steps')
            vals.update({'name': seq})
        result = super(OnboardingSteps, self).create(vals)
        return result

    def open_action_view(self):
        if not self.is_start:
            self.write({
                'is_start': True
            })
        return {
            'name': self.action_id.name,
            'type': 'ir.actions.act_window',
            'res_model': self.action_id.res_model,
            'view_mode': self.action_id.view_mode,
        }

    def step_done(self):
        if not self.is_done:
            self.write({
                'is_done': True
            })
        else:
            self.write({
                'is_done': False
            })
