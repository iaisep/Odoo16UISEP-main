# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import _, models


class OpMeetingWizard(models.TransientModel):
    """  Meeting """
    _name = "op.meeting.wizard"
    _description = "Meeting Wizard"

    def create_meeting(self):
        active_ids = self.env.context.get('active_ids', []) or []
        model = self.env.context.get('active_model')
        partner_ids = self.env.user.partner_id.ids
        if model in ['op.student', 'op.faculty']:
            partner_ids.extend([o_user.partner_id.id for o_user in self.env[
                model].browse(active_ids)])
        if model == "op.parent":
            partner_ids.extend([parent.name.id for parent in self.env[
                model].browse(active_ids)])
        return {
            'name': _('Create Event'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'op.meeting',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'current',
            'nodestroy': True,
            'context': {'default_partner_ids': partner_ids}
        }
