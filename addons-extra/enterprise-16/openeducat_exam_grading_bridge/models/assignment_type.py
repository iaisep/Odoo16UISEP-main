# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import fields, models


class GradingAssigmentType(models.Model):
    _inherit = 'grading.assignment.type'

    assign_type = fields.Selection(selection_add=[('exam', 'Exam')])
