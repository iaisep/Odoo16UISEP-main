# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import fields, models


class OpEvent(models.Model):
    _inherit = "event.event"

    alumni_event_id = fields.Many2one('op.alumni.group', string='Alumni Group')


class Opalumni(models.Model):
    _inherit = "op.alumni.group"

    event_ids = fields.One2many(
        'event.event', 'alumni_event_id', string='Events')
