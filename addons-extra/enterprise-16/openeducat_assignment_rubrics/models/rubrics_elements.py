# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright(C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################
from odoo import fields, models


class OpRubricsElements(models.Model):
    _name = "op.rubric.element"
    _description = "Rubrics Elements Configuration"

    name = fields.Char('Name', required=True)
    rubrics_type = fields.Selection(related='rubrics_template_id.rubrics_type')
    rubrics_template_id = fields.Many2one('op.rubric.template', "Rubric Template")
    description = fields.Text("FeedBack")
    point = fields.Float("Point")
    percentage = fields.Float("Percentage")
