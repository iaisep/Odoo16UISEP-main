# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo.tests import common


class RubricsAssignmentCommon(common.TransactionCase):
    def setUp(self):
        super(RubricsAssignmentCommon, self).setUp()
        self.op_rubric_template = self.env['op.rubric.template']
        self.op_assignment_rubric_sub_line = self.env['op.assignment.rubric.sub.line']
        self.op_assignment_sub_line = self.env['op.assignment.sub.line']
        self.op_assignment = self.env['op.assignment']
