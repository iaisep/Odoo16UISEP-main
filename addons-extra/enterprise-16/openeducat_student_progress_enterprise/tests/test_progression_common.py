# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

import odoo.tests
from odoo.tests import common


class TestProgressionCommon(common.TransactionCase):
    def setUp(self):
        super(TestProgressionCommon, self).setUp()
        self.op_progression = self.env['op.student.progression']


@odoo.tests.tagged('post_install', '-at_install')
class TestUi(odoo.tests.HttpCase):
    def setUp(self):
        super(TestUi, self).setUp()
        student = self.env['res.users'].search(
            [('login', '=', 'student@openeducat.com')])
        student.login = "student"

    def test_01_student_progression(self):
        self.start_tour("/", "test_student_progression", login="student")
