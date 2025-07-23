# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import fields, models


class CourseInvitation(models.TransientModel):
    _name = "course.invitation"
    _description = "LMS Course Invitation"

    user_ids = fields.Many2many(
        'res.users', 'user_course_invitation_rel',
        'invitation_id', 'user_id', string='Users')

    def send_invitation(self):
        parameter = self.env['ir.config_parameter'].sudo().search(
            [('key', '=', 'web.base.url')])
        url = parameter[0].value
        course_url = url + '/courses'
        template_id = self.env.ref(
            'openeducat_lms.email_template_course_invitation_mail')
        user_email = ''
        user = self.env['res.users'].browse(self.env.uid)
        active_id = self.env.context.get('active_id', False)
        course = self.env['op.course'].browse(active_id)
        for user in self.user_ids:
            if user.partner_id and user.partner_id.email:
                if user_email:
                    user_email = user_email + ',' + user.partner_id.email
                else:
                    user_email = user.partner_id.email
        if user_email:
            template_id.email_to = user_email
            body_html = "<p>Hello,</p>\n<p>You are invited from %s to " \
                        "Enroll Course: '%s' .</p>\n%s" % (
                            user.name, course.name, course_url)
            template_id.body_html = body_html
            template_id.send_mail(active_id, force_send=True)
        user_ids = course.invited_users_ids.ids
        invite_uid = self.user_ids.ids
        total_invite_uid = list(set(user_ids + invite_uid))
        course.invited_users_ids = [[6, 0, total_invite_uid]]
        return True
