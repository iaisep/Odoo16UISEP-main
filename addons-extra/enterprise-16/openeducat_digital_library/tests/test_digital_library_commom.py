# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

import odoo.tests
from odoo.tests import common


class TestDigitalLibraryCommon(common.TransactionCase):
    def setUp(self):
        super(TestDigitalLibraryCommon, self).setUp()
        self.op_digital_library_author = self.env['op.digital.library.author']
        self.op_digital_library_publisher = self.env['op.digital.library.publisher']
        self.op_digital_library_category = self.env['op.digital.library.category']
        self.op_digital_library_material = self.env['op.digital.library.material']
        self.op_digital_library_enrollment = self.env['op.digital.library.enrollment']
        self.op_digital_library_material_review = self.\
            env['op.digital.library.material.review']
        self.op_digital_library_material_tag = self.\
            env['op.digital.library.material.tag']


@odoo.tests.tagged('post_install', '-at_install')
class TestUi(odoo.tests.HttpCase):

    def setUp(self):
        super(TestUi, self).setUp()
        stud = self.env['res.users'].search([('login', '=', 'student@openeducat.com')])
        stud.login = 'student'
        parent = self.env['res.users'].search([('login', '=', 'parent@openeducat.com')])
        parent.login = 'parent'

    def test_digital_library(self):
        self.start_tour("/", "digital_library", login="student")
        self.start_tour("/", "digital_library", login="parent")

    def test_category_detail(self):
        self.start_tour("/", "category_detail", login="student")
        self.start_tour("/", "category_detail", login="parent")
