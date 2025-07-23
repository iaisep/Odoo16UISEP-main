# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

{
    'name': 'OpenEduCat Alumni Event Enterprise',
    'summary': """This module adds the feature of event in alumni management system
     to OpenEduCat. You can create event and post it online.""",
    'version': '16.0.1.0',
    'category': 'Education',
    "sequence": 3,
    'complexity': "easy",
    'author': 'OpenEduCat Inc',
    'website': 'http://www.openeducat.org',
    'depends': ['base', 'website_event', 'openeducat_alumni_enterprise'],
    'data': ['views/alumni_event_view.xml',
             'views/alumni_event_template_view.xml',
             'menus/op_menu.xml'
             ],
    'demo': ['demo/event_event_demo.xml',
             'demo/alumni_event_demo.xml'],
    'images': [],
    'assets': {
        'web.assets_tests': [
            '/openeducat_alumni_event_enterprise/'
            'static/tests/tours/alumni_event_test.js'
        ]
    },
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'Other proprietary',
    'live_test_url': 'https://www.openeducat.org/plans'
}
