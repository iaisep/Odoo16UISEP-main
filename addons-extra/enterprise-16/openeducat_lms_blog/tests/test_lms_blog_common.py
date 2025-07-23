# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################
from odoo.tests import common


class TestLmsBlogCommon(common.TransactionCase):
    def setUp(self):
        super(TestLmsBlogCommon, self).setUp()
        self.op_course = self.env['op.course']
        self.blogs = self.env['blog.blog']
        self.blog_posts = self.env['blog.post']
        self.blog_tags = self.env['blog.blog']
