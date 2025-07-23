# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

{
    'name': 'OpenEduCat Placement Job Enterprise',
    'version': '16.0.1.0',
    'category': 'Education',
    "sequence": 3,
    'summary': 'Manage Placement Job',
    'complexity': "easy",
    'author': 'OpenEduCat Inc',
    'website': 'http://www.openeducat.org',
    'depends': ['base',
                'openeducat_core_enterprise',
                'openeducat_skill_enterprise',
                'openeducat_placement_enterprise',
                'openeducat_job_enterprise'],
    'data': ['security/op_security.xml',
             'security/ir.model.access.csv',
             'data/template_mail.xml',
             'data/activity_announcement_data.xml',
             'data/mail_data.xml',
             'views/activity_announcement_detail.xml',
             'views/activity_announcement_apply.xml',
             'views/website_activity_announcement.xml',
             'views/activity_announcement_view.xml',
             'views/job_post_apply_inherit.xml',
             'views/job_applicant_view_inherit.xml',
             'views/placement_cell_view_inherit.xml',
             'menus/op_menu.xml',
             ],
    'demo': ['demo/activity_announcement_demo.xml'],

    'images': [],
    'qweb': [],
    'assets': {
        'web.assets_tests': [
            '/openeducat_placement_job_enterprise/'
            'static/tests/tours/activity_details_test.js',
            '/openeducat_placement_job_enterprise/'
            'static/tests/tours/activity_announcement_apply_test.js',
            '/openeducat_placement_job_enterprise/'
            'static/tests/tours/website_activity_announcement_test.js'
        ]
    },
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'Other proprietary',
    'live_test_url': 'https://www.openeducat.org/plans'
}
