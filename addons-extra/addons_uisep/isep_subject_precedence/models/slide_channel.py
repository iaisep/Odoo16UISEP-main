# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError

class ChannelUsersRelation(models.Model):
    _inherit = 'slide.channel.partner'


    _sql_constraints = [
        ('channel_partner_uniq',
         'check(1=1)',
         'A partner membership to a channel must be unique!'
        ),
    ]


    @api.constrains('channel_id', 'partner_id', 'active')
    def _check_unique_channel_partner_active(self):
        for record in self:
            if record.active:
                # Check for existing active records with the same channel_id and partner_id
                # Exclude the current record itself from the search
                domain = [
                    ('channel_id', '=', record.channel_id.id),
                    ('partner_id', '=', record.partner_id.id),
                    ('active', '=', True),
                    ('id', '!=', record.id) # Exclude self for updates
                ]
                if self.search_count(domain) > 0:
                    raise ValidationError(
                        _("A partner membership for channel '%s' and partner '%s' already exists and is active."
                          % (record.channel_id.name, record.partner_id.name))
                    )




    def _set_as_completed(self, completed=True):
        """ Set record as completed and compute karma gains
        :param completed:
            True if we make the slide as completed
            False if we remove user completion
        """
        res = super()._set_as_completed(completed=completed)
        if completed:
            for record in self.filtered(lambda s: s.admission_id.modality == 'auto'):
                record.admission_id.auto_enroll_student_subject(record.op_subject_id.id)


