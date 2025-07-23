# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import fields, models


class OpPlacementOffer(models.Model):
    _name = "op.placement.cell"
    _inherit = ["mail.thread",
                'website.seo.metadata',
                'website.published.multi.mixin']
    _description = "Placement cell team"

    name = fields.Char('Placement Cell Team', required=True,
                       tracking=True)
    user_id = fields.Many2one('res.users', string='Team Leader',
                              required=True,
                              tracking=True)
    member_ids = fields.One2many('res.users', 'placement_team_id',
                                 string='Channel Members',
                                 tracking=True)
    color = fields.Integer("Color Index", default=0)
    department_id = fields.Many2one(
        'op.department', 'Department',
        default=lambda self:
        self.env.user.dept_id and self.env.user.dept_id.id or False)
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)
    active = fields.Boolean(default=True)
