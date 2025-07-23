# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

{
    'name': 'OpenEduCat LMS Forum',
    'summary': """This module adds the feature of forum in
    learning management system to OpenEduCat.
    You can create forum of course and post it online.""",
    'version': '16.0.1.0',
    'category': 'Education',
    "sequence": 3,
    'complexity': "easy",
    'author': 'OpenEduCat Inc',
    'website': 'http://www.openeducat.org',
    'depends': [
        'website_forum',
        'openeducat_lms',
    ],
    'data': [
        'security/op_sequrity.xml',
        'security/ir.model.access.csv',
        'views/course_view.xml',
        'views/lms_forum_view.xml',
    ],
    'demo': [
        'demo/op_course_forum_data.xml',
    ],
    'images': [
        'static/description/openeducat_lms_forum_banner.jpg',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'Other proprietary',
    'live_test_url': 'https://www.openeducat.org/plans'
}
