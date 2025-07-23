# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import fields, models


class OpGrantBadgeWizard(models.TransientModel):
    _name = "op.badge.student.wizard"
    _description = "Badge Student Wizard"

    student_id = fields.Many2one("op.student", string='Student',
                                 required=True)
    badge_id = fields.Many2one(
        "op.gamification.badge", string='Badge', required=True)
    comment = fields.Text('Comment')

    def action_grant_badge(self):
        for wiz in self:
            self.env['op.badge.student'].create({
                'student_id': wiz.student_id.id,
                'sender_id': self.env.uid,
                'badge_id': wiz.badge_id.id,
                'comment': wiz.comment,
            })
        return True
