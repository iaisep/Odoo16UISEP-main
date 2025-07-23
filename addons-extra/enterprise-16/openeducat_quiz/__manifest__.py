# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

{
    'name': 'OpenEduCat Quiz Management',
    'summary': """Based on best of class enterprise level architecture,
    OpenEduCat is ready to be used from local infrastructure to
    a highly scalable cloud environment.""",
    'version': '16.0.1.0',
    'category': 'Education',
    "sequence": 3,
    'complexity': "easy",
    'author': 'OpenEduCat Inc',
    'website': 'http://www.openeducat.org',
    'depends': [
        'base',
        'portal',
        'gamification',
        'openeducat_core_enterprise',
        'openeducat_web',
        'openeducat_onboarding',
    ],
    'data': [
        'security/op_security.xml',
        'security/ir.model.access.csv',
        'views/category_view.xml',
        'wizard/question_view.xml',
        'wizard/update_mark_view.xml',
        'wizard/override_marks_view.xml',
        'data/quiz_portal_menu.xml',
        'data/portal_result_sequence.xml',
        'views/quiz_view.xml',
        'views/result_view.xml',
        'views/website_view.xml',
        'views/website_view_fullscreen.xml',
        'views/question_bank_view.xml',
        'views/quiz_embeded.xml',
        'views/my_account_result.xml',
        'views/onboard.xml',
        'menus/op_menu.xml',
        'data/onboarding_plan.xml',

    ],
    'demo': [
        'demo/question_bank_type.xml',
        'demo/answer_grade.xml',
        'demo/question_bank.xml',
        'demo/question_bank_math.xml',
        'demo/question_bank_gk.xml',
        'demo/question_bank_c.xml',
        'demo/question_bank_cpp.xml',
        'demo/question_bank_science.xml',
        'demo/question_bank_reference_gk.xml',
        'demo/op_quiz_category_data.xml',
        'demo/op_quiz_data.xml',
        'demo/op_quiz_line_data.xml',
        'demo/op_quiz_result_line.xml',
        'demo/op_quiz_result.xml',
        'demo/demo_quiz1.xml',
        'demo/demo_quiz2.xml',
        'demo/demo_quiz3.xml',
        'demo/demo_quiz4.xml',
        'demo/demo_quiz5.xml',
        'demo/demo_quiz6.xml',
        'demo/op_quiz_demo_30.xml',
        'demo/op_quiz_demo_31.xml',
        'demo/op_quiz_demo_32.xml',
        'demo/op_quiz_demo_33.xml',
        'demo/op_quiz_demo_34.xml',
    ],
    'qweb': [
        'static/src/xml/question.xml',
        ],
    'images': [
        'static/description/openeducat_quiz_banner.jpg',
    ],
    'assets': {
        'web.assets_frontend': [
            '/openeducat_quiz/static/src/scss/website_slides.scss',
            '/openeducat_quiz/static/src/scss/quiz_timer.scss',
            '/openeducat_quiz/static/src/js/website_quiz.js',
            '/openeducat_quiz/static/src/js/quiz_timer.js',
            '/openeducat_quiz/static/src/js/progress.js',
            '/openeducat_quiz/static/src/js/index.js',
            '/openeducat_quiz/static/src/scss/quiz_fullscreen.scss',
            '/openeducat_quiz/static/src/css/index.css',
            '/openeducat_quiz/static/src/xml/question.xml',
        ],
        'web._assets_primary_variables': [
            '/openeducat_quiz/static/src/scss/primary_variables.scss'
        ],
        'openeducat_quiz.slide_embed_assets': [
            'web/static/lib/bootstrap/scss/bootstrap.scss',
            'openeducat_quiz/static/src/scss/website_slides.scss',
            ('include', 'web._assets_helpers'),
            ('include', 'web.pdf_js_lib'),
            '/openeducat_quiz/static/lib/pdfslidesviewer/PDFSlidesViewer.js',
            '/openeducat_quiz/static/src/js/slides_embed.js',
        ],
        'web.assets_tests': [
            '/openeducat_quiz/static/tests/tours/online_exam_test.js',
            '/openeducat_quiz/static/tests/tours/quiz_rules_test.js'
        ]
    },
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'Other proprietary',
    'live_test_url': 'https://www.openeducat.org/plans'
}
