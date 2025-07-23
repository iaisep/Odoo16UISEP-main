# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import http
from odoo.http import request

from odoo.addons.openeducat_lms.controllers.main import OpenEduCatLms


class OpenEduCatLmsForum(OpenEduCatLms):

    @http.route()
    def course(self, course, **kw):
        r = super(OpenEduCatLmsForum, self).course(course, **kw)
        post_ids = request.env['forum.post'].search([
            ('forum_id', '=', course.forum_id.id),
            ('parent_id', '=', False)])
        r.qcontext.update({
            'post_ids': post_ids,
        })
        return r
