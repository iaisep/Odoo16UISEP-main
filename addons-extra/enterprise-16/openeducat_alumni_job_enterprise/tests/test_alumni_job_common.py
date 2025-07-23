# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

import odoo.tests


@odoo.tests.tagged('post_install', '-at_install')
class TestUi(odoo.tests.HttpCase):

    def setUp(self):
        super(TestUi, self).setUp()
        student = self.env['res.users'].search(
            [('login', '=', 'student@openeducat.com')])
        student.login = 'student'
        a = self.env['op.student'].search([('name', '=', 'Sumita S Dani')])
        a.alumni_boolean = True
        parent = self.env['res.users'].search(
            [('login', '=', 'parent@openeducat.com')])
        parent.login = 'parent'

    def test_01_alumni_portal(self):
        self.start_tour("/", "test_alumni_portal", login="student")
        self.start_tour("/", "test_alumni_portal", login="parent")

    def test_01_alumni_job_list(self):
        self.start_tour("/", "test_alumni_job_list", login="student")
        self.start_tour("/", "test_alumni_job_list", login="parent")

    # Below Test Cases are Commented because at that url used Script
    # def test_01_alumni_job(self):
    #     self.start_tour("/", "test_alumni_job", login="student")
    # def test_01_alumni_job_details(self):
    #     self.start_tour("/", "test_alumni_job_details", login="student")
