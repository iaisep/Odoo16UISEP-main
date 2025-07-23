# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright(C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import _, fields, models
from odoo.exceptions import ValidationError


class OpRubricsTemplate(models.Model):
    _name = "op.rubric.template"
    _inherit = ['mail.thread.cc', 'mail.activity.mixin']
    _description = "Rubrics Template Configuration"

    name = fields.Char('Name', required=True)
    rubric_element_line = fields.One2many('op.rubric.element',
                                          'rubrics_template_id',
                                          'Rubrics Elements')
    rubrics_type = fields.Selection(
        [('no_points', 'No Points'),
         ('points', 'Points'),
         ('percent', 'Percent')],
        'Rubrics type', default="points",
        required=True)
    state = fields.Selection(
        [('draft', 'Draft'),
         ('in_use', 'In Use'),
         ('cancel', 'Cancelled'),
         ('re_open', 'Re-open')],
        'State', default="draft", tracking=True)

    def act_in_use(self):
        self.state = 'in_use'
        if self.rubrics_type == 'percent':
            total = []
            for current_template in self.rubric_element_line:
                total.append(current_template.percentage)
            total_marks = 100
            sum_marks = sum(total)
            if sum_marks < total_marks:
                raise ValidationError(_(
                    "The Total of the distributed percentage is less then 100%."
                    " Please distribute the percentage properly."))

    def act_cancel(self):
        self.state = 'cancel'

    def act_re_open(self):
        self.state = 'draft'
