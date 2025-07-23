# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

{
    'name': 'OpenEduCat Exam Enterprise',
    'summary': """Exam is very important part of any educational institute.
    Exam module from OpenEduCat helps you managing most of
    the exam details very easily using Exam module.""",
    'version': '16.0.1.0',
    'category': 'Education',
    "sequence": 3,
    'complexity': "easy",
    'author': 'OpenEduCat Inc',
    'website': 'http://www.openeducat.org',
    'depends': [
        'openeducat_exam',
        'openeducat_core_enterprise',
        'openeducat_student_progress_enterprise',
        'openeducat_onboarding',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/op_security.xml',
        'data/exam_portal_menu.xml',
        'views/exam_view.xml',
        'views/exam_attendees_view.xml',
        'views/result_template_view.xml',
        'views/marksheet_register_view.xml',
        'views/marksheet_line_view.xml',
        'views/result_line_view.xml',
        'views/exam_room_view.xml',
        'views/exam_type_view.xml',
        'views/exam_dashboard_view.xml',
        'dashboard/exam_dashboard.xml',
        'wizards/progression_marksheet_wizard_view.xml',
        'views/exam_session_view.xml',
        'views/exam_onbaord.xml',
        'views/openeducat_exam_portal.xml',
        'views/openeducat_marksheet_line_view.xml',
        'views/openeducat_progression_marksheet_line.xml',
        'views/student_progression_exam_portal.xml',
        'reports/exam_progression_report.xml',
        'data/onboarding_plan.xml',
    ],
    'demo': [
        'demo/progression_marksheet_demo.xml',
    ],
    'images': [
        'static/description/openeducat_exam_enterprise_banner.jpg',
    ],
    'qweb': [],
    'assets': {
        'web.assets_tests': [
            '/openeducat_exam_enterprise/static/tests/tours/test_student_exam.js',
            '/openeducat_exam_enterprise/static/tests/tours/test_student_exam_data.js',
        ],
        'web.assets_backend': [
            '/openeducat_exam_enterprise/static/src/scss/styles.scss',
            '/openeducat_exam_enterprise/static/src/js/Chart.min.js'
        ],
        'web.assets_qweb': [
            '/openeducat_exam_enterprise/static/src/xml/*.xml',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'Other proprietary',
    'live_test_url': 'https://www.openeducat.org/plans'
}
