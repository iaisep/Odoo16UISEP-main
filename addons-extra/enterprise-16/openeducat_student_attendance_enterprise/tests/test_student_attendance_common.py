# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################
from odoo.tests import common


class TestStudentAttendanceCommon(common.TransactionCase):
    def setUp(self):
        super(TestStudentAttendanceCommon, self).setUp()
        self.op_student_attendance_line = self.env['op.attendance.line']
        self.op_student = self.env['op.student']
