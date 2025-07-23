# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import _, exceptions, fields, models


class OpOverrideMark(models.TransientModel):
    _name = "op.override.mark"
    _description = "Override Mark Wizard"

    override = fields.Boolean("Override", default=True)
    override_marks = fields.Float(store=True)

    def action_confirm_mark(self):
        self.ensure_one()
        line = self.env['op.quiz.result'].browse(
            self.env.context.get('active_id'))
        if self.override_marks > line.total_marks or self.override_marks < 0:
            raise exceptions.ValidationError(_('Set proper marks.'))
        else:
            line.override = self.override
            line.received_marks = self.override_marks
            line.score = (line.received_marks * 100) / line.total_marks
