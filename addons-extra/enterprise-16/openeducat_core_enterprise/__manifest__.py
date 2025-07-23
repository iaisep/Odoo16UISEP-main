# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

{
    'name': 'OpenEduCat Core Enterprise',
    'summary': """Based on best of class enterprise level architecture,
    OpenEduCat is ready to be used from local infrastructure
    to a highly scalable cloud environment.""",
    'version': '16.0.1.0',
    'category': 'Education',
    "sequence": 1,
    'complexity': "easy",
    'author': 'OpenEduCat Inc',
    'website': 'http://www.openeducat.org',
    'depends': [
        'calendar',
        'website',
        'gamification',
        'openeducat_core',
        'openeducat_web',
        'openeducat_onboarding'
        # 'openeducat_rest'
    ],
    'data': [
        'security/op_security.xml',
        'security/ir.model.access.csv',
        'wizard/op_grant_badge_wizard_view.xml',
        'data/portal_menu_data.xml',
        'report/report_menu.xml',
        'report/report_student_information.xml',
        'report/report_student_course_enrollment.xml',
        'views/batch_view.xml',
        'views/academic_calendar_inherit.xml',
        'views/student_view.xml',
        'views/res_config_settings.xml',
        'views/faculty_view.xml',
        'views/subject_view.xml',
        'views/student_badge_view.xml',
        'views/openeducat_personal_info_portal.xml',
        'views/openeducat_educational_info_portal.xml',
        'views/board_affiliation_view.xml',
        'views/op_section_view.xml',
        'views/onboard.xml',
        'views/openeducat_subject_registration_portal.xml',
        'dashboard/openeducat_dashboard_view.xml',
        'views/course_view.xml',
        'views/subject_registration_analysis.xml',
        'data/onboarding_plan.xml',
        'views/course_catagory_view.xml',
        'menu/course_menu.xml'
    ],
    'demo': [
        'demo/student_badge_demo.xml',
        'demo/course_subject_demo.xml',
        'demo/res_users_demo.xml',
        'demo/op_course_category_data.xml',
    ],
    'css': [],
    'js': [],
    'images': [
        'static/description/openeducat_core_enterprise_banner.jpg',
    ],
    'assets': {
        'web.assets_frontend': [
            '/openeducat_core_enterprise/static/src/js/custom.js',
            '/openeducat_core_enterprise/static/src/js/portal_academic_timetable.js',
            '/openeducat_core_enterprise/static/src/css/web_conf.css',
            '/openeducat_core_enterprise/static/src/scss/student_profile.scss',
            '/openeducat_core_enterprise/static/src/xml/custom.xml',
        ],
        'website.assets_wysiwyg': [
            '/openeducat_core_enterprise/static/src/components/configurator/'
            'configurator.js',
        ],
        'web.assets_qweb':
            [
                '/openeducat_core_enterprise/static/src/components/configurator/'
                'configurator.xml',
                '/openeducat_core_enterprise/static/src/xml/custom.xml',
                '/openeducat_core_enterprise/static/src/xml/theme_preview.xml',
                # 'website/static/src/components/configurator/configurator.xml',
            ],
        'web.assets_tests': [
            '/openeducat_core_enterprise/static/tests/tours/'
            'student_profile_test.js',
            '/openeducat_core_enterprise/static/tests/tours/'
            'subject_registration_test.js'
        ]
    },
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'Other proprietary',
    'live_test_url': 'https://www.openeducat.org/plans'
}
