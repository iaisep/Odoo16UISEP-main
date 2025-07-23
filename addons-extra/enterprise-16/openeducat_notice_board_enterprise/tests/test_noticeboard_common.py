# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo.tests import TransactionCase
from odoo.tests.common import HttpCase, tagged


class TestNoticeBoardCommon(TransactionCase):
    def setUp(self):
        super(TestNoticeBoardCommon, self).setUp()

        self.op_notice = self.env['op.notice']
        self.op_circular = self.env['op.circular']
        self.op_notice_group = self.env['op.notice.group']


@tagged('post_install', '-at_install')
class TestUi(HttpCase):

    def setUp(self):
        super(TestUi, self).setUp()
        student = self.env['res.users'].search(
            [('login', '=', 'student@openeducat.com')])
        student.login = "student"
        parent = self.env['res.users'].search(
            [('login', '=', 'parent@openeducat.com')])
        parent.login = "parent"

    def test_01_notice_board_notice(self):
        self.start_tour("/", "student_notice_list_view", login="student")
        self.start_tour("/", "parent_notice_list_view", login="parent")
        self.start_tour("/", "student_notice_view", login="student")
        self.start_tour("/", "parent_notice_view", login="parent")

    def test_01_notice_board_circular(self):
        self.start_tour("/", "student_circular_list_view", login="student")
        self.start_tour("/", "parent_circular_list_view", login="parent")
