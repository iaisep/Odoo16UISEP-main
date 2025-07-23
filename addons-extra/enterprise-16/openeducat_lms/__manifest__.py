# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################


{
    'name': 'OpenEduCat LMS',
    'summary': """This module adds the feature of learning management system
    to OpenEduCat. You can create online course and publish it.""",
    'version': '16.0.1.0',
    'category': 'Education',
    "sequence": 3,
    'complexity': "easy",
    'author': 'OpenEduCat Inc',
    'website': 'http://www.openeducat.org',
    'depends': [
        'portal',
        'website_mail',
        'portal_rating',
        'auth_signup',
        'openeducat_core',
        'openeducat_quiz',
        'openeducat_onboarding',
    ],
    'data': [
        'security/op_security.xml',
        'security/ir.model.access.csv',
        'wizard/course_invitation_view.xml',
        'data/course_invitation.xml',
        'data/material_reminder.xml',
        'data/auth_signup.xml',
        'data/report_paperformat.xml',
        'data/certificate_sequence.xml',
        'views/quiz_view.xml',
        'views/course_level_view.xml',
        'views/course_view.xml',
        'views/faculty_view.xml',
        'views/course_detail.xml',
        'views/course_material.xml',
        'views/course_enrollment_view.xml',
        'views/website_lms.xml',
        'views/lms_embed.xml',
        'views/material_detail_view.xml',
        'views/my_courses.xml',
        'views/lms_onboard.xml',
        'views/certificate_portal.xml',
        'views/course_section_view.xml',
        'views/course_section_material_view.xml',
        'reports/course_reports.xml',
        'reports/course_certificate_templates.xml',
        'dashboard/lms_dashboard.xml',
        'menus/op_menu.xml',
        'data/onboarding_plan.xml',
    ],
    'demo': [
        'demo/op_course_level_demo.xml',
        'demo/op_material_data.xml',
        'demo/op_course_data.xml',
        'demo/op_course_section_data.xml',
        'demo/op_course_material_data.xml',
        'demo/res_users_data.xml',
        'demo/enrollement_demo_data.xml',
        'demo/rating_message_data.xml',
        'demo/op_course_demo2.xml',
        'demo/op_course_demo1.xml',
        'demo/op_course_demo3.xml',
        'demo/op_course_demo4.xml',
        'demo/op_course_demo5.xml',
        'demo/op_course_demo6.xml',
        'demo/op_course_demo_30.xml',
        'demo/op_course_demo_32.xml',
        'demo/op_course_demo_33.xml',
        'demo/op_course_demo_34.xml',
        'demo/op_course_demo_35.xml',
    ],
    'images': [
        'static/description/openeducat_lms_banner.jpg',
    ],
    'qweb': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'assets': {
        'web.assets_qweb': [
            '/openeducat_lms/static/src/xml/navbar.xml',
        ],
        'web.assets_backend': [
            '/openeducat_lms/static/src/scss/account_contract_dashboard.scss',
            '/openeducat_lms/static/src/js/openeducat_lms_dashboard.js'
        ],
        'web.assets_tests': [
            '/openeducat_lms/static/tests/tours/lmscontest.js',
            '/openeducat_lms/static/tests/tours/course_details_test.js'
        ],
        'web.assets_frontend': [
            '/openeducat_lms/static/src/scss/owl.carousel.css',
            '/openeducat_lms/static/src/scss/lms_common.scss',
            '/openeducat_lms/static/src/js/owl.carousel.js',
            '/openeducat_lms/static/src/js/carousel_slider.js',
            '/openeducat_lms/static/src/js/category_menu.js',
            '/openeducat_lms/static/src/js/progress.js',
            '/openeducat_lms/static/src/js/expand_screen.js',
            '/openeducat_lms/static/src/js/open-modal.js',
            '/openeducat_lms/static/src/xml/openmodal.xml'
        ],
        'website.assets_editor': [
            '/openeducat_lms/static/src/js/new_content.js'

        ],
        'openeducat_lms.slide_embed_assets': [
            'web/static/lib/bootstrap/scss/bootstrap.scss',
            'openeducat_lms/static/src/scss/website_slides.scss',
            ('include', 'web.pdf_js_lib'),
            'openeducat_lms/static/lib/pdfslidesviewer/PDFSlidesViewer.js',
            'openeducat_lms/static/src/js/slides_embed.js'],
        'website._assets_primary_variables': [
            '/openeducat_lms/static/src/scss/primary_variables.scss'
        ],
    },
    'license': 'Other proprietary',
    'live_test_url': 'https://www.openeducat.org/plans'
}
