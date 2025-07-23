# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

{
    'name': 'OpenEduCat LMS Sale',
    'summary': """This module adds the feature in OpenEduCat LMS
    to sell courses online.""",
    'version': '16.0.1.0',
    'category': 'Education',
    "sequence": 3,
    'complexity': "easy",
    'author': 'OpenEduCat Inc',
    'website': 'http://www.openeducat.org',
    'depends': [
        'website_sale',
        'openeducat_lms',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/course_view.xml',
        'views/course_enrollment_view.xml',
    ],
    'demo': [
        'demo/lms_sale_data.xml',

    ],
    'images': [
        'static/description/openeducat_lms_sale_banner.jpg',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'Other proprietary',
    'live_test_url': 'https://www.openeducat.org/plans'
}
