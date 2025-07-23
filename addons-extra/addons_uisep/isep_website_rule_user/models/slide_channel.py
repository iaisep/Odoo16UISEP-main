# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class SlideChannel(models.Model):
    _inherit = 'slide.channel'


    users_added = fields.Boolean(string="Usuarios Agregados", default=False)


    def action_add_users_odoo(self):
        if self.visibility not in ('members'):
            raise UserError(_('Esta función sólo es para miembros!'))
        if self.enroll not in ('public'):
            raise UserError(_('Esta función sólo es para registro público!'))

        slide_channel_partner = self.env['slide.channel.partner']
        users = self.env['res.users']

        active_users = users.search([('active', '=', True), ('share', 'in', [True, False]), ('partner_id', '!=', False)])

        for user in active_users:
            existing_record = slide_channel_partner.search_count([
                ('partner_id', '=', user.partner_id.id),
                ('channel_id', '=', self.id)
            ])
            
            if existing_record == 0:
                slide_channel_partner.create({
                    'partner_id': user.partner_id.id,
                    'channel_id': self.id,
                    'auto_added': True,
                })

        self.users_added = True



    def action_remove_users_odoo(self):
        slide_channel_partner = self.env['slide.channel.partner']
        users = self.env['res.users']

        active_users = users.search([('active', '=', True), ('share', 'in', [True, False])])

        records_to_delete = slide_channel_partner.search([
            ('partner_id', 'in', active_users.mapped('partner_id').ids),
            ('channel_id', '=', self.id),
            ('auto_added', '=', True)
        ])
        records_to_delete.unlink()

        self.users_added = False