from datetime import datetime
from random import choice

from werkzeug.urls import url_encode

from odoo import api, fields, models


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    def action_create_meet(self):
        if self.channel_id:
            url = str(self.get_base_url())+'/web#%s' % url_encode({
                'action':
                self.env['ir.model.data']._xmlid_to_res_id('mail.action_discuss'),
                'default_active_id': "mail.box_inbox",
                'active_id': 'mail.channel_'+str(self.channel_id.id),
                'menu_id':
                self.env['ir.model.data']._xmlid_to_res_id('mail.menu_root_discuss'),
            })
            self.start = datetime.now()
            self.stop = datetime.now()
            return {
                'type': 'ir.actions.client',
                'tag': 'create_meet_calendar',
                'context': {'url': url, 'id': self.id,
                            'channel': self.channel_id.id, 'name': self.name},
                'params': {'reload': 1, 'meeting_id': self.id}
            }
        else:
            channel = self.env['mail.channel'].\
                create({'name': self.name,
                        'public': 'public',
                        'default_display_mode': 'video_full_screen',
                        'is_password': "12345678",
                        'is_lockpassword': True,
                        })

            # channel.channel_last_seen_partner_ids.is_host = True
            self.channel_id = channel.id

    def create_password(self):
        is_password = ''.join(
            choice('abcdefghijkmnopqrstuvwxyzABCDEFGHIJKLMNPQRSTUVWXYZ23456789')
            for _i in range(10))
        return is_password

    @api.onchange('is_meeting')
    def onchange_create_meeting(self):
        if self.name and self.is_meeting:
            password = self.create_password()
            if not self.channel_id:
                channel = self.env['mail.channel'].\
                    create({'name': self.name,
                            'default_display_mode': 'video_full_screen',
                            'is_password': password,
                            'is_lockpassword': True,
                            })

                # channel.channel_last_seen_partner_ids.is_host = True
                url = str(self.get_base_url())+'/chat/' + \
                    str(channel.id)+'/'+str(channel.uuid)
                self.videocall_location = url
                self.is_password = password
                self.online_meeting = True
                self.write({'channel_id': channel.id})
                moderator_password = self.create_password()
                self.mpw = moderator_password

                for attendee in self.attendee_ids:
                    if self.user_id.partner_id == attendee.partner_id:
                        attendee.write({
                            'attendee_meeting_url': url,
                            'apw': password
                        })
                    else:
                        attendee.write({
                            'attendee_meeting_url': url,
                            'apw': password
                        })
                channel._broadcast(self.env.user.partner_id.id)
                return channel.channel_info()[0]
            else:
                self.videocall_location = str(self.get_base_url(
                ))+'/chat/' + str(self.channel_id.id)+'/'+str(self.channel_id.uuid)
                self.is_password = self.channel_id.is_password
        else:
            self.videocall_location = ''
            self.is_password = ''

    def write(self, vals):
        res = super(CalendarEvent, self).write(vals)
        self.channel_id.name = self.name
        if self.channel_id:
            for record in self.partner_ids:
                channel_members = self.channel_id.channel_member_ids
                if not channel_members.filtered(lambda c:
                                                record._origin.id == c.partner_id.id):
                    self.env['mail.channel.member'].sudo().create({
                        'partner_id': record._origin.id,
                        'channel_id': self.channel_id.id,
                    })
        if self.is_password:
            self.channel_id.is_lockpassword = True
            self.channel_id.is_password = self.is_password
        else:
            self.channel_id.is_lockpassword = False
        vals.update({'videocall_location': self.videocall_location})
        for attendee in self.attendee_ids:
            if self.user_id.partner_id == attendee.partner_id:
                attendee.write({
                    'attendee_meeting_url': self.videocall_location,
                    'apw': self.is_password
                })
            else:
                attendee.write({
                    'attendee_meeting_url': self.videocall_location,
                    'apw': self.is_password
                })

        return res

    @api.model_create_multi
    def create(self, vals):
        res = super(CalendarEvent, self).create(vals)
        res.channel_id.calendar_id = res.id
        res.channel_id.name = res.name
        if self.channel_id:
            for record in self.partner_ids:
                channel_members = self.channel_id.channel_member_ids
                if not channel_members.filtered(lambda c:
                                                record._origin.id == c.partner_id.id):
                    self.env['mail.channel.member'].sudo().create({
                        'partner_id': record._origin.id,
                        'channel_id': self.channel_id.id,
                    })
        res.onchange_create_meeting()
        return res

    def unlink(self):
        for record in self:
            if record.channel_id:
                record.channel_id.sudo().unlink()
        return super(CalendarEvent, self).unlink()

    is_start_meeting = fields.Boolean(
        string="Is Start meeeting", default=False)
    is_password = fields.Char(string="Password")
    is_meeting = fields.Boolean(string="Create Meeting", default=False)
    channel_id = fields.Many2one('mail.channel')
    course_id = fields.Many2one('op.course', string="Course")
    subject_id = fields.Many2one('op.subject', string="Subject")
    batch_id = fields.Many2one('op.batch', string="Batch")


class MailChannelPartner(models.Model):
    _inherit = 'mail.channel.member'

    is_host = fields.Boolean(string="is host")
