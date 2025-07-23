# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class OpCourse(models.Model):
    _inherit = "op.course"

    forum_id = fields.Many2one('forum.forum', 'Forum')
    forum_post_ids = fields.One2many('forum.post', 'course_id',
                                     string='Forum Post')
    forum_count = fields.Integer(compute='_compute_forum_count', store=True)

    @api.depends("forum_post_ids")
    def _compute_forum_count(self):
        for record in self:
            record.forum_count = len(record.forum_post_ids)

    def action_create_forum(self):
        for record in self:
            if self.env.user.karma < 7:
                raise ValidationError(
                    _('It appears your email has not been verified to \
                    participate in forum, Verify it from forum menu on \
                    homepage.'))
            if not record.forum_id:
                record.forum_id = self.env['forum.forum'].sudo().create(
                    {'name': record.name})
        return True

    def get_forum(self):
        action = self.env.ref('website_forum.'
                              'action_forum_post').read()[0]
        action['domain'] = [('forum_id', 'in', self.forum_id.ids)]
        return action
