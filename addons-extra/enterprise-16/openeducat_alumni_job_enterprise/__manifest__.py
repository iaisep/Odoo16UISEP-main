# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

{
    'name': 'OpenEduCat Alumni Job Enterprise',
    'summary': """This module allows alumni to create job post.""",
    'version': '16.0.1.0',
    'category': 'Education',
    "sequence": 3,
    'complexity': "easy",
    'author': 'OpenEduCat Inc',
    'website': 'http://www.openeducat.org',
    'depends': ['base',
                'openeducat_alumni_enterprise',
                'openeducat_job_enterprise',
                'openeducat_skill_enterprise',
                'openeducat_job_skill_bridge'],
    'data': ['data/alumni_portal_menu.xml',
             'views/alumni_job_post_view.xml',
             'views/alumani_job_post_portal.xml',
             'menus/op_menu.xml'],
    'demo': ['demo/job_post.xml'],
    'images': [],
    'assets': {
        'web.assets_frontend': [
            '/openeducat_alumni_job_enterprise/static/src/js/datepicker.js',
            '/openeducat_alumni_job_enterprise/static/src/js/delete_content.js',
            '/openeducat_alumni_job_enterprise/static/src/js/custom.js'

        ],
        'web.assets_tests': [
            '/openeducat_alumni_job_enterprise/'
            'static/tests/tours/alumni_job_portal_test.js',
            '/openeducat_alumni_job_enterprise/'
            'static/tests/tours/alumni_job_details_test.js',
            '/openeducat_alumni_job_enterprise/'
            'static/tests/tours/alumni_job_list_test.js',
            '/openeducat_alumni_job_enterprise/'
            'static/tests/tours/alumni_job_test.js',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'Other proprietary',
    'live_test_url': 'https://www.openeducat.org/plans'
}
