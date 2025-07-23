# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import models


class Partner(models.Model):
    _inherit = "res.partner"

    def get_attendee_detail(self, meeting_id):
        """ Return a list of tuple (id, name, status)
        Used by web_calendar.js : Many2ManyAttendee
        """
        datas = []
        for partner in self:
            data = partner.name_get()[0]
            datas.append([data[0], data[1], False, partner.color])
        return datas
