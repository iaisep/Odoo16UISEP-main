# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import fields, models


class OpMeeting(models.Model):
    _name = "op.meeting"
    _inherit = "mail.thread"
    _inherits = {"calendar.event": "meeting_id"}
    _description = "Meeting"

    meeting_id = fields.Many2one('calendar.event', 'Meeting',
                                 required=True, ondelete='cascade')
