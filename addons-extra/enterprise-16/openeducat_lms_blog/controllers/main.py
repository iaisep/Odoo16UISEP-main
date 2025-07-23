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
        blog_post_ids = request.env['blog.post'].search([
            ('blog_id', '=', course.blog_id.id)])
        r.qcontext.update({
            'blog_post_ids': blog_post_ids,
        })
        return r
