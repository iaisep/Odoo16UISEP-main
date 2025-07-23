# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

{
    'name': "OpenEduCat Admission Enterprise",
    'summary': """This module allows you to manage admission process efficiently.
     You can set fees details & adds constrains to admission process through
     admission register.""",
    'version': '16.0.1.0',
    'category': 'Education',
    'sequence': 3,
    'complexity': "easy",
    'author': 'OpenEduCat Inc',
    'website': 'http://www.openeducat.org',
    'depends': [
        'openeducat_admission',
        'openeducat_core_enterprise'
    ],
    'data': [
        'security/op_security.xml',
        'data/invoice_cron.xml',
        'data/mail_data.xml',
        'views/admission_view.xml',
        'views/openeducat_dashboard_view.xml',
        'views/admission_register.xml',
        'data/invoice_bills_portal_menu.xml',
        'views/onboard.xml'
    ],
    'demo': [],
    'css': [],
    'qweb': [],
    'js': [],
    'images': [
        'static/description/openeducat_admission_enterprise_banner.jpg',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'Other proprietary',
    'live_test_url': 'https://www.openeducat.org/plans'
}
