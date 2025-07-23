# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

{
    'name': 'OpenEduCat LMS Blog',
    'summary': """This module adds the feature of blog in learning management
    system to OpenEduCat. You can create blog of course and post it online.""",
    'version': '16.0.1.0',
    'category': 'Education',
    "sequence": 3,
    'complexity': "easy",
    'author': 'OpenEduCat Inc',
    'website': 'http://www.openeducat.org',
    'depends': [
        'website_blog',
        'openeducat_lms',
    ],
    'data': [
        'security/op_sequrity.xml',
        'security/ir.model.access.csv',
        'views/blog_post_view.xml',
        'views/course_view.xml',
        'views/lms_blog_view.xml',
    ],
    'demo': [
        'demo/blog_demo_data.xml',
        'demo/blog_tag_demo_data.xml',
        'demo/blog_post_demo_data.xml'
    ],
    'images': [
        'static/description/openeducat_lms_blog_banner.jpg',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'Other proprietary',
    'live_test_url': 'https://www.openeducat.org/plans'
}
