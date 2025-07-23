# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

{
    'name': 'OpenEduCat Meeting Enterprise',
    'version': '16.0.1.0',
    'category': 'Education',
    "sequence": 3,
    'summary': 'Manage Meeting',
    'complexity': "easy",
    'author': 'OpenEduCat Inc',
    'website': 'http://www.openeducat.org',
    'depends': [
        'calendar',
        'openeducat_parent',
        'openeducat_core_enterprise',
    ],
    'data': [
        'security/op_security.xml',
        'data/meeting_portal_menu.xml',
        'security/ir.model.access.csv',
        'wizard/op_meeting_wizard_view.xml',
        'views/op_meeting_view.xml',
        'views/res_partner_category_data.xml',
        'views/onboard.xml',
        'views/openeduact_meeting_portal.xml',
    ],
    'demo': [
        'demo/calendar_event_type_data.xml',
        'demo/op_meeting_demo.xml',
    ],
    'images': [
        'static/description/openeducat_meeting_enterprise_banner.jpg',
    ],
    'assets': {
        'web.assets_tests': [
            '/openeducat_meeting_enterprise/'
            'static/tests/tours/meeting_information_data_test.js'
        ],
        'web.assets_frontend': [
            '/openeducat_meeting_enterprise/static/src/js/portal_meeting.js'
        ]
    },
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'Other proprietary',
    'live_test_url': 'https://www.openeducat.org/plans'
}
