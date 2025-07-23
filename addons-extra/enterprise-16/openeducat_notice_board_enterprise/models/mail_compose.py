# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import api, models


class NoticeMailCompose(models.TransientModel):
    _inherit = 'mail.compose.message'

    @api.model
    def default_get(self, fields):
        res = super(NoticeMailCompose, self).default_get(fields)
        context = dict(self.env.context)
        recipient = []
        if self.env.context.get('active_model') == 'op.circular':
            active_ids = context.get('active_ids', []) or []
            records = self.env['op.circular'].browse(active_ids)
            for student in records.group_id.student_ids:
                if student.partner_id.id:
                    recipient.append(student.partner_id.id)

            for parent in records.group_id.parent_ids:
                if parent.name.id:
                    recipient.append(parent.name.id)

            for faculty in records.group_id.faculty_ids:
                if faculty.emp_id.user_partner_id.id:
                    recipient.append(faculty.emp_id.user_partner_id.id)
            res['partner_ids'] = [(6, 0, recipient)]

        elif self.env.context.get('active_model') == 'op.notice':
            active_ids = context.get('active_ids', []) or []
            records = self.env['op.notice'].browse(active_ids)
            for student in records.group_id.student_ids:
                if student.partner_id.id:
                    recipient.append(student.partner_id.id)

            for parent in records.group_id.parent_ids:
                if parent.name.id:
                    recipient.append(parent.name.id)

            for faculty in records.group_id.faculty_ids:
                if faculty.emp_id.user_partner_id.id:
                    recipient.append(faculty.emp_id.user_partner_id.id)
            res['partner_ids'] = [(6, 0, recipient)]
        return res
