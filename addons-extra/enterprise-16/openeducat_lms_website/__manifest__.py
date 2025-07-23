# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

{
    'name': 'OpenEduCat LMS Website',
    'summary': """This module allows you to add videos, quizzes, presentations,
    webpages and H5p contents directly via portal side.""",
    'version': '16.0.1.0',
    'category': 'Education',
    "sequence": 3,
    'complexity': "easy",
    'author': 'OpenEduCat Inc',
    'website': 'http://www.openeducat.org',
    'depends': [
        'openeducat_lms',
    ],
    'data': [
        'views/course_detail_website.xml',
        'data/website_data.xml',

    ],
    'demo': [],
    'images': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'assets': {
        'web.assets_frontend': [
            '/openeducat_lms_website/static/src/js/course_section_add.js',
            '/openeducat_lms_website/static/src/js/material_upload.js',
            '/openeducat_lms_website/static/src/xml/material_upload.xml',
            '/openeducat_lms_website/static/src/xml/course_section.xml'
        ],
        'website.assets_editor': [
            '/openeducat_lms_website/static/src/js/lms_course.editor.js'
        ],
    },

    'license': 'Other proprietary',
    'live_test_url': 'https://www.openeducat.org/plans'
}
