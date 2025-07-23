# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import api, fields, models


class OpQuiz(models.Model):
    _inherit = "op.quiz"

    lms = fields.Boolean('LMS')

    @api.onchange('lms')
    def _onchange_lms(self):
        (self.single_que, self.show_result) = (True, True) \
            if self.lms else (False, False)
