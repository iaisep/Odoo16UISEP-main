# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import http
from odoo.http import request

from odoo.addons.openeducat_assignment_enterprise.controller.main import (
    SubmitAssignment,
)
from odoo.addons.portal.controllers.portal import CustomerPortal


class SubmitAssignment(CustomerPortal):

    @http.route()
    def portal_submit_assignment(self, assignment_id=None, student_id=None, **kw):
        res = super(SubmitAssignment, self).\
            portal_submit_assignment(assignment_id, student_id, **kw)

        marks = request.render('openeducat_assignment_grading_enterprise.'
                               'assignment_marks_view')

        res.qcontext.update({'marks': marks})

        return res
