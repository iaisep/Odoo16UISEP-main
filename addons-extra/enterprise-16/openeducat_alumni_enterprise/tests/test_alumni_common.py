# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

import odoo.tests
from odoo.tests import common


class TestAlumniCommon(common.TransactionCase):
    def setUp(self):
        super(TestAlumniCommon, self).setUp()
        self.op_alumni_group = self.env['op.alumni.group']
        self.op_alumni = self.env['op.student']


@odoo.tests.tagged('post_install', '-at_install')
class TestUi(odoo.tests.HttpCase):
    def setUp(self):
        super(TestUi, self).setUp()
        stud = self.env['res.users'].search([('login', '=', 'student@openeducat.com')])
        stud.login = "student"
        parent = self.env['res.users'].search([('login', '=', 'parent@openeducat.com')])
        parent.login = "parent"

    def test_alumni_page(self):
        self.start_tour("/", "alumni_page", login="student")
        self.start_tour("/", "alumni_page", login="parent")

    def test_alumni_detail(self):
        self.start_tour("/", 'alumni_detail', login="student")
        self.start_tour("/", 'alumni_detail', login="parent")
