# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

{
    'name': 'OpenEduCat Student Progress Enterprise',
    'summary': """This module provides the facility of the
    Student Progression Report which help the admin and faculty to create
    the student progression report of all the activities that the student has
    participated and the student can see their progression
    by logging into their account.""",
    'version': '16.0.1.0',
    'category': 'Education',
    "sequence": 4,
    'complexity': "easy",
    'author': 'OpenEduCat Inc',
    'website': 'http://www.openeducat.org',
    'depends': [
        'openeducat_core_enterprise',

    ],
    'data': [
        'data/ir_sequence.xml',
        'data/student_progress_portal_menu.xml',
        'security/op_security.xml',
        'security/ir.model.access.csv',
        'report/student_progression_report.xml',
        'report/report_menu.xml',
        'views/op_student_progress_portal.xml',
        'views/op_student_progress_data.xml',
        'menu/progress_menu.xml',
    ],
    'demo': ['demo/student_progression_demo.xml'],
    'css': [],
    'qweb': [],
    'js': [],
    'images': [

    ],
    'assets': {
        'web.assets_tests': [
            '/openeducat_student_progress_enterprise/'
            'static/tests/tours/student_progression_test.js'
        ],
        'website.assets_frontend': [
            '/openeducat_student_progress_enterprise/'
            'static/src/scss/student_progress.scss'
        ]
    },
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'Other proprietary',
    'live_test_url': 'https://www.openeducat.org/plans'
}
