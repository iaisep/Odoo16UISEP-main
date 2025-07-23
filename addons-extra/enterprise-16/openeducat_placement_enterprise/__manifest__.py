# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

{
    'name': 'OpenEduCat Placement Enterprise',
    'version': '16.0.1.0',
    'category': 'Education',
    "sequence": 3,
    'summary': 'Manage Placement',
    'complexity': "easy",
    'author': 'OpenEduCat Inc',
    'website': 'http://www.openeducat.org',
    'depends': ['base',
                'openeducat_core_enterprise'],
    'data': [
        'security/op_security.xml',
        'security/ir.model.access.csv',
        'views/placement_view.xml',
        'views/placement_cell_view.xml',
        'views/openeducat_placement_portal.xml',
        'menus/op_menu.xml',
    ],
    'demo': [
        'demo/placement_offer_demo.xml',
        'demo/placement_cell_view_demo.xml',
    ],
    'images': [
        'static/description/openeducat_placement_enterprise_banner.jpg',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'Other proprietary',
    'live_test_url': 'https://www.openeducat.org/plans'
}
