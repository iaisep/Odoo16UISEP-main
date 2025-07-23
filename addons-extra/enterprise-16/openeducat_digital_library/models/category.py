# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################
from odoo import api, fields, models


class OpDigitalLibraryCategory(models.Model):
    _name = 'op.digital.library.category'
    _description = 'Category Of Material'
    _rec_name = 'display_name'

    name = fields.Char(string="Name", required=True)
    material_ids = fields.Many2many('op.digital.library.material', string="Material")
    material_count = fields.Integer('Total Material',
                                    compute="_compute_get_total_material_count")
    parent_id = fields.Many2one('op.digital.library.category',
                                string="Parent Category")
    display_name = fields.Char(string="Display Name",
                               compute="_compute_category_display_name", store=True)

    @api.depends('material_ids')
    def _compute_get_total_material_count(self):
        for record in self:
            if record.material_ids:
                record.material_count = len(record.material_ids)
            else:
                record.material_count = 0

    @api.depends('name', 'parent_id')
    def _compute_category_display_name(self):
        for record in self:
            name = record.name if record.name else ''
            if record.parent_id:
                record.display_name = record.parent_id.display_name + ' / ' + name
            else:
                record.display_name = name
