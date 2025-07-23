# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

{
    'name': 'OpenEduCat LMS Gamification',
    'summary': """This module adds the feature of gamification in
    learning management system to OpenEduCat.
    You can create survey on course.""",
    'version': '16.0.1.0',
    'category': 'Education',
    "sequence": 3,
    'complexity': "easy",
    'author': 'OpenEduCat Inc',
    'website': 'http://www.openeducat.org',
    'depends': [
        'gamification', 'website_profile',
        'openeducat_lms'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/course_view.xml',
        'views/gamification_badges_view.xml',
        'views/web_gamification_view.xml',
        'menus/op_menu.xml',
        'menus/badge_portal_menu.xml'
    ],
    'demo': [
        'demo/challenges_data.xml'
    ],
    'images': [
        'static/description/openeducat_lms_gamification_banner.jpg',
    ],
    'assets': {
        'web.assets_frontend': [
            '/openeducat_lms_gamification/static/src/scss/gamification_common.scss'
        ]
    },
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'Other proprietary',
    'live_test_url': 'https://www.openeducat.org/plans'
}
