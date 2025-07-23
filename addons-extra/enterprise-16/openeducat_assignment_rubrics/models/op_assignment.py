# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright(C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class OpAssignment(models.Model):
    _inherit = "op.assignment"

    rubric_template_id = fields.Many2one("op.rubric.template",
                                         "Rubrics Template",
                                         domain="[('state','=', 'in_use')]")

    @api.constrains('rubric_template_id')
    def _check_marks(self):
        if self.rubric_template_id:
            current_list = []
            if self.rubric_template_id.rubrics_type == 'points':
                for current_template in self.rubric_template_id.rubric_element_line:
                    current_list.append(current_template.point)
                if sum(current_list) < self.point:
                    raise ValidationError(_("The Total of the distributed"
                                            " Points in the current"
                                            " template is less then"
                                            " total marks of assignment."
                                            " Please distribute"
                                            " the points properly."))
                elif sum(current_list) > self.point:
                    raise ValidationError(_("The Total of the distributed"
                                            " Points in the current"
                                            " template is greater then"
                                            " total marks of assignment."
                                            " Please distribute the"
                                            " points properly."))

            elif self.rubric_template_id.rubrics_type == 'percent':
                for current_template in self.rubric_template_id.rubric_element_line:
                    current_list.append(current_template.percentage)
                if sum(current_list) < 100.00:
                    raise ValidationError(_("The Total of the"
                                            " distributed percentage"
                                            " in the current template"
                                            " is less than 100%."
                                            " Please distribute"
                                            " the percentage properly."))
                elif sum(current_list) > 100.00:
                    raise ValidationError(_("The Total of the"
                                            " distributed percentage"
                                            " in the current template"
                                            " is greater than 100%."
                                            " Please distribute"
                                            " the percentage properly."))
