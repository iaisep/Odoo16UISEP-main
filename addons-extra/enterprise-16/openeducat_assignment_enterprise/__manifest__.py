# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

{
    'name': 'OpenEduCat Assignment Enterprise',
    'summary': """This module allows you to manage the assignments easily.
    Faculty can create assignment, publish it & student can make submission
    for that.""",
    'version': '16.0.1.0',
    'category': 'Education',
    "sequence": 3,
    'complexity': "easy",
    'author': 'OpenEduCat Inc',
    'website': 'http://www.openeducat.org',
    'depends': [
        'openeducat_assignment',
        'openeducat_core_enterprise',
        'openeducat_student_progress_enterprise',
        'openeducat_onboarding',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/op_security.xml',
        'wizards/progression_assignment_wizard_view.xml',
        'views/openeducat_assignment_portal.xml',
        'views/assignment_view.xml',
        'views/assignment_type_view.xml',
        'views/assignment_sub_line_view.xml',
        'views/assignment_onboard.xml',
        'views/submit_assignment_portal.xml',
        'views/openeducat_assignment_view.xml',
        'views/openeducat_progression_assignment.xml',
        'views/student_progression_assignment_portal.xml',
        'views/course_view.xml',
        'views/faculty_view.xml',
        'views/subject_view.xml',
        'data/assignment_portal_menu.xml',
        'reports/assignment_progression_report.xml',
        'data/onboarding_plan.xml',
    ],
    'demo': ['demo/progression_assignment_demo.xml',
             'demo/assignment_demo.xml'],
    'images': [
        'static/description/openeducat_assignment_enterprise_banner.jpg',
    ],
    'assets': {
        'web.assets_tests': [
            '/openeducat_assignment_enterprise/static/tests/tours/test_assignment.js',
            '/openeducat_assignment_enterprise/'
            'static/tests/tours/test_assignment_submit.js'
        ]},
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'Other proprietary',
    'live_test_url': 'https://www.openeducat.org/plans'
}
