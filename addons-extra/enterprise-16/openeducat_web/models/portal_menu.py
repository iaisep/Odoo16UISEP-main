# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import api, fields, models


class PortalMenu(models.Model):
    _name = "openeducat.portal.menu"
    _description = "Portal Menu"
    _order = "sequence, id"
    _rec_name = 'name'

    def _default_sequence(self):
        menu = self.search([], limit=1, order="sequence DESC")
        return menu.sequence or 0

    website_id = fields.Many2one('website', 'Website', ondelete='cascade')
    sequence = fields.Integer('Sequence', default=_default_sequence)
    name = fields.Char('Menu', required=True, translate=True)
    link = fields.Char('Link', default='')
    icon_code = fields.Char('Icon-Code')
    active = fields.Boolean('Visible On The Portal')
    is_visible_to_student = fields.Boolean('Visible On The Student', default=True)
    is_visible_to_parent = fields.Boolean('Visible On The Parent', default=True)
    is_visible = fields.Boolean(compute='_compute_visible', string='Is Visible')
    group_ids = fields.Many2many('res.groups', string='Visible Groups')
    background_color = fields.Char(string="Background Color",
                                   default="#02b0e0")
    icon_image = fields.Image('Icon Image')
    menu_ref_name = fields.Char(string="Ref name")

    @api.model_create_multi
    def create(self, vals_list):
        self.clear_caches()
        for vals in vals_list:
            current_website = self.env['website'].get_current_website()
            vals['website_id'] = current_website.id
        res = super(PortalMenu, self).create(vals_list)
        return res

    def _compute_visible(self):
        for menu in self:
            visible = True
            if menu.user_has_groups('base.group_user'):
                visible = False

            menu.is_visible = visible

    # @api.onchange('name')
    # def onchange_ref_name(self):
    #     for rec in self:
    #         rec.ref_id = rec.name
