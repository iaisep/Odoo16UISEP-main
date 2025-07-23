# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

{
    'name': 'OpenEduCat Web',
    'version': '16.0.1.0',
    'category': 'Education',
    "sequence": 1,
    'summary': 'Manage Students, Faculties and Education Institute',
    'complexity': "easy",
    'author': 'OpenEduCat Inc',
    'website': 'http://www.openeducat.org',
    'depends': [
        'web',
        'openeducat_core',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_config_param_data.xml',
        'views/res_config_setting_view.xml',
        'views/webclient_templates.xml',
        'views/openeducat_portal_menu.xml',
        'views/openeducat_student_portal_menus.xml',
    ],
    'demo': [
    ],
    'css': [],
    'qweb': [],
    'js': [
    ],
    'images': [
        'static/description/openeducat_enterprise_banner.jpg',
    ],
    'assets': {
        'web.assets_backend': [
            #'/openeducat_web/static/src/js/annoying_notification.js',
            '/openeducat_web/static/src/js/one_signal.js',
            #'openeducat_web/static/src/js/review.js',
            #'/openeducat_web/static/src/scss/annoying_notification.scss',
            '/openeducat_web/static/src/xml/menu_content.xml',
            '/openeducat_web/static/src/xml/subscription.xml',
        ],
        'web.assets_frontend': [
            '/openeducat_web/static/src/scss/portal_view.scss',
            '/openeducat_web/static/src/js/portal_view.js',
            '/openeducat_web/static/src/js/one_signal.js'
        ],
        'web.assets_qweb': [
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'Other proprietary',
    'live_test_url': 'https://www.openeducat.org/plans'
}
