# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################
from odoo.tests import common


class TestLessonCommon(common.TransactionCase):
    def setUp(self):
        super(TestLessonCommon, self).setUp()
        self.op_lesson = self.env['op.lesson']
