# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

import odoo.tests
from odoo.tests.common import TransactionCase


class GMSCommon(TransactionCase):
    def setUp(self):
        super(GMSCommon, self).setUp()

    def test_data(self):
        self.grivance = self.env['grievance']
        self.grivance_category = self.env['grievance.category']
        self.grievance_root_cause = self.env['grievance.root.cause']
        self.grievance_team = self.env['grievance.team']
        self.grievance_action = self.env['wizard.action.taken']


@odoo.tests.tagged('post_install', '-at_install')
class TestUi(odoo.tests.HttpCase):

    def setUp(self):
        super(TestUi, self).setUp()
        student = self.env['res.users'].search(
            [('login', '=', 'student@openeducat.com')])
        student.login = "student"
        parent = self.env['res.users'].search(
            [('login', '=', 'parent@openeducat.com')])
        parent.login = "parent"
        faculty = self.env['res.users'].search(
            [('login', '=', 'faculty@openeducat.com')])
        faculty.login = "faculty"

    def test_gms_grievance_detail(self):
        self.start_tour("/", 'test_gms_grievance_detail', login="student")
        self.start_tour("/", 'test_gms_parent_grievance_detail', login="parent")
        self.start_tour("/", 'test_gms_faculty_grievance_detail', login="faculty")

    def test_gms_all_grievance(self):
        self.start_tour("/", 'test_gms_all_grievance', login="student")
        self.start_tour("/", 'test_gms_parent_all_grievance', login="parent")
        self.start_tour("/", 'test_gms_faculty_all_grievance', login="faculty")

    def test_gms_grievance_submit(self):
        self.start_tour("/", 'test_gms_grievance_submit', login="student")
        self.start_tour("/", 'test_gms_grievance_submit_state', login="student")
        data = self.env['grievance'].search(
            [('id', '=',
              self.ref('openeducat_grievance_enterprise.gms_grievance_object1'))])
        data.state = 'resolve'
        self.start_tour("/", 'test_gms_grievance_satisfied', login="student")
        data.state = 'resolve'
        self.start_tour("/", 'test_gms_grievance_not_satisfied', login="student")
        self.start_tour("/", 'test_gms_grievance_appeal_submit', login="student")
        self.start_tour("/", 'test_gms_parent_grievance_submit', login="parent")
        self.start_tour("/", 'test_gms_parent_grievance_submit_state', login="parent")
        parent_data = self.env['grievance'].search(
            [('id', '=',
              self.ref('openeducat_grievance_enterprise.gms_grievance_object3'))])
        parent_data.state = 'resolve'
        self.start_tour("/", 'test_gms_parent_grievance_satisfied', login="parent")
        parent_data.state = 'resolve'
        self.start_tour("/", 'test_gms_parent_grievance_not_satisfied', login="parent")
        self.start_tour("/", 'test_gms_faculty_grievance_submit', login="faculty")
        self.start_tour("/", 'test_gms_faculty_grievance_submit_state', login="faculty")

    def test_gms_grievance_edit(self):
        self.start_tour("/", 'test_gms_grievance_edit', login="student")
        self.start_tour("/", 'test_gms_parent_grievance_edit', login="parent")
        self.start_tour("/", 'test_gms_faculty_grievance_edit', login="faculty")

    def test_gms_grievance_delete(self):
        data = self.env['grievance'].search(
            [('id', '=',
              self.ref('openeducat_grievance_enterprise.gms_grievance_object1'))])
        data.state = 'draft'
        self.start_tour("/", 'test_gms_grievance_delete', login="student")
        parent_data = self.env['grievance'].search(
            [('id', '=',
              self.ref('openeducat_grievance_enterprise.gms_grievance_object3'))])
        parent_data.state = 'draft'
        self.start_tour("/", 'test_gms_parent_grievance_delete', login="parent")
