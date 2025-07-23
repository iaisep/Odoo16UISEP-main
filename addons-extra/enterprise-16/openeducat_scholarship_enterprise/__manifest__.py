# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

{
    'name': 'OpenEduCat Scholarship Enterprise',
    'summary': """This module allows you to have details for
     scholarship of students.""",
    'version': '16.0.1.0',
    'category': 'Education',
    "sequence": 3,
    'complexity': "easy",
    'author': 'OpenEduCat Inc',
    'website': 'http://www.openeducat.org',
    'depends': ['openeducat_core_enterprise', 'account', ],
    'data': [
        'security/op_security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'views/scholarship_stages_view.xml',
        'views/scholarship_view.xml',
        'views/scholarship_type_view.xml',
        'menus/op_menu.xml',
    ],
    'demo': [
        'demo/scholarship_stages.xml',
        'demo/scholarship_type_demo.xml',
        'demo/scholarship_demo.xml',

    ],
    'images': [
        'static/description/openeducat_scholarship_enterprise_banner.jpg',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'Other proprietary',
    'live_test_url': 'https://www.openeducat.org/plans'
}
