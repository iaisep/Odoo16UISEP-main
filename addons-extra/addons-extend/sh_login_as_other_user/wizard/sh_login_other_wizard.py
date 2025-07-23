# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import fields, models
from odoo.exceptions import UserError, ValidationError


SCOPE = 'sh_login'


class LoginUserWizard(models.TransientModel):
    _name = 'login.other.wizard'
    _description = "Used to Login From Other User"
    sh_user_id = fields.Many2one("res.users", string="Login As")
    sh_group_ids = fields.Many2many(
        "res.groups", related="sh_user_id.groups_id", string="Groups")

    def action_do_login(self):
        self.ensure_one()
        #    base.group_portal
        #    base.group_public
        #    base.group_user

        user_type = self.sh_user_id.has_group('base.group_user')
        # raise UserError(str(user_type))
        if self.env.user.has_group('sh_login_as_other_user.sh_allow_login_as_other_user_only_portal') and user_type:
            raise UserError('Solo puede cambiar a cuentas de tipo Portal')

        return {
            'type': 'ir.actions.act_url',
            'url': '/web/sh_login?uid=%s' % self.sh_user_id.id,
            'target': 'self',
        }
