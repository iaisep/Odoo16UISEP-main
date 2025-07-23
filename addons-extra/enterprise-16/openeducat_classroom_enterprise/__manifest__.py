# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

{
    'name': 'OpenEduCat Classroom Enterprise',
    'summary': """This module allows you to manage classroom details.""",
    'version': '16.0.1.0',
    'category': 'Education',
    "sequence": 3,
    'complexity': "easy",
    'author': 'OpenEduCat Inc',
    'website': 'http://www.openeducat.org',
    'depends': [
        'openeducat_classroom',
        'openeducat_core_enterprise',
        'openeducat_onboarding',
    ],
    'data': [
        'security/op_security.xml',
        'views/classroom_view.xml',
        'data/onboarding_plan.xml',
    ],
    'demo': [
    ],
    'images': [
        'static/description/openeducat_classroom_enterprise_banner.jpg',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'Other proprietary',
    'live_test_url': 'https://www.openeducat.org/plans'
}
