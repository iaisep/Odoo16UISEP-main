# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright(C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################
from odoo import api, fields, models


class Meeting(models.Model):
    _inherit = 'calendar.event'

    op_session_id = fields.Many2one('op.session', string="Session")
    mpw = fields.Char("Moderator Password")
    meeting_url = fields.Char("URL")
    online_meeting = fields.Boolean("Online Meeting", copy=False)
    automatic_email = fields.Boolean('Automatic Email')

    @api.model_create_multi
    def create(self, values_list):
        res_param = self.env['ir.config_parameter'].sudo()
        auto_email = res_param.search([
            ('key', '=', 'calendar.automaticemail')])
        for values in values_list:
            values['automatic_email'] = auto_email
        meeting = super(Meeting, self).create(values_list)
        return meeting

    def create_attendees(self):
        current_user = self.env.user
        result = {}
        for meeting in self:
            alreay_meeting_partners = meeting.attendee_ids.mapped('partner_id')
            meeting_attendees = self.env['calendar.attendee']
            meeting_partners = self.env['res.partner']
            for partner in meeting.partner_ids.filtered(
                    lambda partner: partner not in alreay_meeting_partners):
                values = {
                    'partner_id': partner.id,
                    'email': partner.email,
                    'event_id': meeting.id,
                }

                if self._context.get('google_internal_event_id', False):
                    values['google_internal_event_id'] = \
                        self._context.get('google_internal_event_id')

                if partner == self.env.user.partner_id:
                    values['state'] = 'accepted'

                attendee = self.env['calendar.attendee'].create(values)

                meeting_attendees |= attendee
                meeting_partners |= partner

            if meeting.automatic_email is True:
                if meeting_attendees and not self._context.get('detaching'):
                    to_notify = meeting_attendees. \
                        filtered(lambda a: a.email != current_user.email)
                    to_notify._send_mail_to_attendees(
                        'calendar.calendar_template_meeting_invitation')

            if meeting_attendees:
                meeting.write({'attendee_ids': [
                    (4, meeting_attendee.id)
                    for meeting_attendee in meeting_attendees]})

            if meeting_partners:
                meeting.message_subscribe(partner_ids=meeting_partners.ids)

            all_partners = meeting.partner_ids
            all_partner_attendees = meeting.attendee_ids.mapped('partner_id')
            old_attendees = meeting.attendee_ids
            partners_to_remove = \
                all_partner_attendees + meeting_partners - all_partners

            attendees_to_remove = self.env["calendar.attendee"]
            if partners_to_remove:
                attendees_to_remove = self.env["calendar.attendee"].search(
                    [('partner_id', 'in', partners_to_remove.ids),
                     ('event_id', '=', meeting.id)])
                attendees_to_remove.unlink()

            result[meeting.id] = {
                'new_attendees': meeting_attendees,
                'old_attendees': old_attendees,
                'removed_attendees': attendees_to_remove,
                'removed_partners': partners_to_remove
            }
        return result


class Attendee(models.Model):
    _inherit = 'calendar.attendee'

    attendee_meeting_url = fields.Char('URL')
    apw = fields.Char("Attendee Password")


class OpSession(models.Model):
    _inherit = 'op.session'

    def _compute_get_meetings(self):
        for record in self:
            record.meeting_count = self.env['calendar.event'].search_count(
                [('op_session_id', 'in', self.ids)])

    meeting_count = fields.Integer(string='Meeting Count',
                                   compute='_compute_get_meetings', readonly=True)

    def action_view_online_meetings(self):

        event_ids = self.env['calendar.event'].search(
            [('op_session_id', 'in', self.ids)])

        action = self.env.ref('calendar.action_calendar_event').sudo().read()[0]

        osc_ids = self.env['op.student.course'].search((
            ['course_id', '=', self.course_id.id],
            ['batch_id', '=', self.batch_id.id],
        ))
        student_partner_ids = [osc.student_id.partner_id.id for osc in osc_ids]
        if len(event_ids) >= 1:
            action['domain'] = [('op_session_id', 'in', self.ids)]
        # elif len(event_ids) == 1:
        else:
            form_view = [
                (self.env.ref('calendar.view_calendar_event_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [
                    (state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = event_ids.id

        context = {
        }
        if len(self) == 1:
            partner_ids = student_partner_ids or []
            partner = self.env.user.partner_id
            partner_ids.append(partner.id)
            for rec in self:
                for rec1 in rec.user_ids:
                    partner_ids.append(rec1.partner_id.id)
            context.update({
                'default_partner_id': self.faculty_id.partner_id.id,
                'default_name': self.name,
                'default_start': self.start_datetime,
                'default_stop': self.end_datetime,
                'default_partner_ids': [[6, 0, list(set(partner_ids))]],
                'default_user_id': self.faculty_id.user_id.id,
                'default_op_session_id': self.id
            })

        action['context'] = context
        return action

    def create_online_meeting(self):
        action = self.env.ref('calendar.'
                              'action_calendar_event').read()[0]
        action['domain'] = [('op_session_id', 'in', self.ids)]
        return action
