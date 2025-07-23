# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import fields, models


class OpBadgeStudent(models.Model):
    _name = "op.badge.student"
    _description = "Gamification Student badge"
    _order = "create_date desc"
    _rec_name = "badge_name"

    student_id = fields.Many2one(
        'op.student', string="Student", required=True,
        ondelete="cascade", index=True)
    sender_id = fields.Many2one(
        'res.users', string="Sender", help="The user who has send the badge")
    badge_id = fields.Many2one(
        'op.gamification.badge', string='Badge', required=True,
        ondelete="cascade", index=True)
    comment = fields.Text('Comment')
    badge_name = fields.Char(related='badge_id.name', string="Badge Name")
    create_date = fields.Datetime('Created', readonly=True)


class OpGamificationBadge(models.Model):
    _name = "op.gamification.badge"
    _description = "Gamification Badge"

    name = fields.Char('Badge', required=True, translate=True)
    active = fields.Boolean('Active', default=True)
    description = fields.Text('Description', translate=True)
    image = fields.Image(
        "Image", attachment=True, help="This field holds the image \
        used for the badge, limited to 256x256")
