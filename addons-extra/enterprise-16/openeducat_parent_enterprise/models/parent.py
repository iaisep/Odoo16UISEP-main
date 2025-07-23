# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import fields, models


class OpParent(models.Model):
    _name = 'op.parent'
    _inherit = ["op.parent", "mail.thread", 'mail.activity.mixin']

    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)
    tag_ids = fields.Many2many("res.partner.category", string="Tags")
    name = fields.Many2one('res.partner', 'Name', required=True,
                           tracking=True)

    def action_onboarding_parent_layout(self):
        self.env.user.company_id.core_onboarding_parent_layout_state = 'done'
