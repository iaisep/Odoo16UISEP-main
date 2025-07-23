from odoo import fields, models


class MailRtcsession(models.Model):
    _inherit = "mail.channel.rtc.session"

    is_screen_show = fields.Boolean(string="Has disabled screen share")
    is_hand_raised = fields.Boolean(string="Has hand raised")
    is_Emoji = fields.Char(string="Has emoji", default="")
    is_badgeemoji = fields.Char(string="Has badge emoji", default="")
    is_Attentiveness = fields.Boolean(string="Has change tab")

    def _update_and_broadcast(self, values):
        """ Updates the session and notifies all members of the channel
            of the change.
        """
        valid_values = {'is_screen_sharing_on', 'is_camera_on', 'is_muted', 'is_deaf',
                        'is_hand_raised',
                        'is_screen_show', 'is_Emoji', 'is_Attentiveness'}
        self.write({key: values[key]
                   for key in valid_values if key in valid_values and key in values})
        session_data = self._mail_rtc_session_format()
        self.env['bus.bus']._sendone(self.channel_id, 'mail.channel.rtc.session/insert',
                                     session_data)

    def update_and_emoji(self, values, session_id):
        valid_values = {'is_badgeemoji'}
        self.write({key: values[key]
                   for key in valid_values if key in valid_values})
        session_data = self._mail_rtc_session_emoji(session_id)
        self.env['bus.bus']._sendone(self.channel_id, 'mail.channel.rtc.session/insert',
                                     session_data)

    def _mail_rtc_session_emoji(self, session_id):
        vals = {
            'id': int(session_id),
            'isbadgeemoji': self.is_badgeemoji,
        }
        if self.guest_id:
            vals['guest'] = [('insert', {
                'id': self.guest_id.id,
                'name': self.guest_id.name,
            })]
        else:
            vals['partner'] = [('insert', {
                'id': self.partner_id.id,
                'name': self.partner_id.name,
            })]
        return vals

    def _mail_rtc_session_format(self, fields=None):
        self.ensure_one()
        res = super(MailRtcsession, self)._mail_rtc_session_format(fields)
        res.update({
            'id': self.id,
            'isCameraOn': self.is_camera_on,
            'isDeaf': self.is_deaf,
            'isMuted': self.is_muted,
            'isScreenSharingOn': self.is_screen_sharing_on,
            'isHandRaised': self.is_hand_raised,
            'isEmoji': self.is_Emoji,
            'isAttentiveness': self.is_Attentiveness,
        })
        return res
