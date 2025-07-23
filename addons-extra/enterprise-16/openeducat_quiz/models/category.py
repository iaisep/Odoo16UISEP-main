# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import _, api, fields, models


class OpQuizCategory(models.Model):
    _name = "op.quiz.category"
    _description = "Quiz Category"

    name = fields.Char('Name')
    code = fields.Char('Code')
    description = fields.Text('Description')
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)
    active = fields.Boolean(default=True)

    @api.model
    def get_import_templates(self):
        return [{
            'label': _('Import Template for Quiz Category'),
            'template': '/openeducat_quiz/static/xls/quiz_category.xls'
        }]
