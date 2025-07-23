# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

{
    'name': 'OpenEduCat Timetable Enterprise',
    'summary': """This module adds feature to manage the session to OpenEduCat.""",
    'version': '16.0.1.0',
    'category': 'Education',
    "sequence": 3,
    'complexity': "easy",
    'author': 'OpenEduCat Inc',
    'website': 'http://www.openeducat.org',
    'depends': [
        'openeducat_lesson',
        'openeducat_timetable',
        'openeducat_core_enterprise'
    ],
    'data': [
        'security/op_security.xml',
        'views/timetable_view.xml',
        'views/timing_view.xml',
        'views/openeducat_dashboard_view.xml',
        'views/timetable_onboard.xml',
        'views/openeducat_timetable_portal.xml',
        'views/course_dashboard.xml',
        'views/course_view.xml',
        'views/subject_view.xml',
        'views/student_course_details.xml',
        'views/faculty_view.xml',
        'menu/timetable_portal_menu.xml',
    ],
    'demo': [],
    'css': [],
    'qweb': [],
    'js': [],
    'images': [
        'static/description/openeducat_timetable_enterprise_banner.jpg',
    ],
    'assets': {
        'web.assets_frontend': [
            '/openeducat_timetable_enterprise/static/src/js/portal_timetable.js',
            '/openeducat_timetable_enterprise/static/tests/tours/timetable_test.js'
        ]
    },
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'Other proprietary',
    'live_test_url': 'https://www.openeducat.org/plans'
}
