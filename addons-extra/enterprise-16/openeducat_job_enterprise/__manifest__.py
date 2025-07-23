# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

{
    'name': 'OpenEduCat Job Enterprise',
    'version': '16.0.1.0',
    'category': 'Education',
    "sequence": 3,
    'summary': 'Manage Job',
    'complexity': "easy",
    'author': 'OpenEduCat Inc',
    'website': 'http://www.openeducat.org',
    'depends': ['base',
                'openeducat_core_enterprise',
                'website'],
    'data': ['security/op_security.xml',
             'security/ir.model.access.csv',
             'data/job_post_code.xml',
             'data/config_data.xml',
             'data/job_applicant_code.xml',
             'views/job_applicant_view.xml',
             'views/job_post_view.xml',
             'views/job_type_view.xml',
             'views/student_view.xml',
             'views/web_job_post_view.xml',
             'views/job_post_apply_template.xml',
             'views/openeducat_student_job_post_portal.xml',
             'views/stages_demo.xml',
             'menus/op_menu.xml'],
    'demo': ['demo/job_type_demo.xml',
             'demo/job_post_view_demo.xml',
             'demo/job_post_applicant_demo.xml'],
    'images': [],
    'qweb': [],
    'assets': {
        'web.assets_backend': [
            '/openeducat_job_enterprise/static/src/scss/ribbon_color.scss'
        ],
        'web.assets_frontend': [
            '/openeducat_job_enterprise/static/src/scss/job_post_view.scss'
        ],
        'web._assets_primary_variables': [
            '/openeducat_job_enterprise/static/src/scss/primary_variables.scss'
        ],
        'web.assets_tests': [
            '/openeducat_job_enterprise/static/tests/tours/job_post_test.js',
            '/openeducat_job_enterprise/static/tests/tours/campus_jobs_test.js',
            '/openeducat_job_enterprise/static/tests/tours/job_post_apply_test.js',
            '/openeducat_job_enterprise/static/tests/tours/job_post_description.js',
        ]
    },
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'Other proprietary',
    'live_test_url': 'https://www.openeducat.org/plans'
}
