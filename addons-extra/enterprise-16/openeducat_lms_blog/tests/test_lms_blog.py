# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from logging import info

from .test_lms_blog_common import TestLmsBlogCommon


class TestLmsBlog(TestLmsBlogCommon):

    def setUp(self):
        super(TestLmsBlog, self).setUp()

    def course_details(self, course):
        info('Course Details for : %s' % course.name)
        if not course.blog_id.name:
            raise AssertionError(
                'Error in data, please check blog data for : %s' % course.name)
        info('  Blog : %s' % course.blog_id.name)
        if not course.blog_post_ids:
            raise AssertionError(
                'There is no any post available for this blog')
        info('  Posts Details:.....')
        for post in course.blog_post_ids:
            info('      Title : %s' % post.name)
            info('      Subtitle : %s' % post.subtitle)
            info('      Website Published : %s' % post.website_published)
            info('      Published Date : %s' % post.published_date)
            info('      Website Meta Keywords : '
                 '%s' % post.website_meta_keywords)
            info('      Website Meta Description: '
                 '%s' % post.website_meta_description)
            info('      Tags Details:.....')
            if not course.blog_post_ids.tag_ids:
                raise AssertionError('Please check for tags')
            for tag in course.blog_post_ids.tag_ids:
                info('          Name : %s' % tag.name)

    def test_blog_1(self):
        courses = [self.env.ref('openeducat_lms.demo_course_1'),
                   self.env.ref('openeducat_lms.demo_course_3')]

        for course in courses:
            self.course_details(course)


class TestCourseBlog(TestLmsBlogCommon):

    def setUp(self):
        super(TestCourseBlog, self).setUp()

    def test_op_course(self):
        course = self.op_course.search([])
        course.action_create_blog()
