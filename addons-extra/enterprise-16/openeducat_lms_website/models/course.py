# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import api, fields, models


class OpCourse(models.Model):
    _inherit = "op.course"

    can_upload = fields.Boolean('Can Upload',
                                compute='_compute_can_upload', compute_sudo=False)

    @api.depends('user_id')
    @api.depends_context('uid')
    def _compute_can_upload(self):
        for record in self:
            if record.user_id == self.env.user:
                record.can_upload = True
            else:
                record.can_upload = self.env.user.has_group(
                    'website.group_website_publisher')

    @api.depends('user_id', 'can_upload')
    def _compute_can_publish(self):
        for record in self:
            if not record.can_upload:
                record.can_publish = False
            elif record.user_id == self.env.user or self.env.is_superuser():
                record.can_publish = True
            else:
                record.can_publish = self.env.user.has_group(
                    'website.group_website_publisher')


class OpCourseSection(models.Model):
    _inherit = "op.course.section"

    seq = fields.Integer("seq", default=0)
