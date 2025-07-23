# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

{
    'name': 'OpenEduCat Alumni Enterprise',
    'summary': """This module allows you to manage details of alumni
     of institute.""",
    'version': '16.0.1.0',
    'category': 'Education',
    "sequence": 3,
    'complexity': "easy",
    'author': 'OpenEduCat Inc',
    'website': 'http://www.openeducat.org',
    'depends': ['base', 'openeducat_core_enterprise', 'website_profile',
                'website_forum', 'product', 'account'],
    'data': [
        'security/op_security.xml',
        'security/ir.model.access.csv',
        'views/alumni_view.xml',
        'views/alumni_group_view.xml',
        'views/web_alumni_view.xml',
        'views/student_template_view.xml',
        'menus/op_menu.xml'],
    'demo': [
        'demo/product_demo.xml',
        'demo/student_demo.xml',
        'demo/alumni_group_demo.xml'
    ],
    'images': [
        'static/description/openeducat_alumni_enterprise_banner.jpg',
    ],
    'assets': {
        'web.assets_tests': [
            '/openeducat_alumni_enterprise/static/tests/tours/alumni_group_test.js',
            '/openeducat_alumni_enterprise/static/tests/tours/alumni_detail_test.js'
        ],
        'web.assets_frontend': [
            '/openeducat_alumni_enterprise/static/src/scss/alumni_view.scss'
        ],
        # 'web._assets_primary_variables': [
        #     '/openeducat_alumni_enterprise/static/src/scss/primary_variables.scss'
        # ]
    },
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'Other proprietary',
    'live_test_url': 'https://www.openeducat.org/plans'
}
