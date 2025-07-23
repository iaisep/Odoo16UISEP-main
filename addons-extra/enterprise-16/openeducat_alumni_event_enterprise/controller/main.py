# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import http
from odoo.http import request

from odoo.addons.openeducat_alumni_enterprise.controller.main import AlumniWeb


class AlumniEvent(AlumniWeb):

    @http.route()
    def alumni_detail(self, alumni, **kwargs):
        response = super(AlumniEvent, self).alumni_detail(alumni=alumni,
                                                          **kwargs)
        event = request.env["event.event"]
        alumnievents = event.sudo().search([('id', 'in', alumni.event_ids.ids)
                                            ])
        response.qcontext.update({
            'alumnievents': alumnievents,
        })
        return response
