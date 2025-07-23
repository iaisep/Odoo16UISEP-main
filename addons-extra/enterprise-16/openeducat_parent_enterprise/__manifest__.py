# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

{
    'name': 'OpenEduCat Parent Enterprise',
    'version': '16.0.1.0',
    'category': 'Education',
    "sequence": 3,
    'summary': 'Manage Parent',
    'complexity': "easy",
    'author': 'OpenEduCat Inc',
    'website': 'http://www.openeducat.org',
    'depends': ['openeducat_core_enterprise', 'openeducat_parent'],
    'data': [
        'security/op_security.xml',
        'views/parent_view.xml',
        'views/parent_onboard.xml',
        'views/openeducat_parent_portal.xml',
        'views/openeducat_root_parent_portal.xml',
    ],
    'demo': [
    ],
    'images': [
        'static/description/openeducat_parent_enterprise_banner.jpg',
    ],
    'assets': {
        'web.assets_frontend': [
            '/openeducat_parent_enterprise/static/src/scss/portal_view.scss',
            '/openeducat_parent_enterprise/static/src/js/portal_view.js'
        ],
        'web.assets_tests': [
            '/openeducat_parent_enterprise/static/tests/tours/my_child_test.js'
        ]

    },
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'Other proprietary',
    'live_test_url': 'https://www.openeducat.org/plans'
}
