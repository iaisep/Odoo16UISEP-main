# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

{
    'name': "OpenEduCat Grievance Enterprise",
    'version': '16.0.1.0',
    'summary': "Manage Grievance",
    'author': "OpenEduCat Inc",
    'website': 'http://www.openeducat.org',
    'category': 'Education',
    "sequence": 3,
    'depends': ['base',
                'openeducat_core_enterprise',
                'openeducat_parent_enterprise', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'data/mail_template.xml',
        'wizard/wizard_action_taken_view.xml',
        'views/grievance_category_views.xml',
        'views/grievance_views.xml',
        'views/grievance_team_views.xml',
        'views/grievance_template.xml',
        'views/grievance_portal_menu.xml',
        'menu/menu.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_tests': [
            "/openeducat_grievance_enterprise/static/tests"
            "/tours/test_gms_grievance_detail.js",
            "/openeducat_grievance_enterprise/static/tests"
            "/tours/test_gms_all_grievance.js",
            "/openeducat_grievance_enterprise/static/tests"
            "/tours/test_gms_grievance_submit.js",
            "/openeducat_grievance_enterprise/static/tests"
            "/tours/test_gms_grievance_edit.js",
            "/openeducat_grievance_enterprise/static/tests"
            "/tours/test_gms_grievance_delete.js",
            "/openeducat_grievance_enterprise/static/tests"
            "/tours/test_gms_parent_grievance_detail.js",
            "/openeducat_grievance_enterprise/static/tests"
            "/tours/test_gms_parent_all_grievance.js",
            "/openeducat_grievance_enterprise/static/tests"
            "/tours/test_gms_parent_grievance_edit.js",
            "/openeducat_grievance_enterprise/static/tests"
            "/tours/test_gms_parent_grievance_delete.js",
            "/openeducat_grievance_enterprise/static/tests"
            "/tours/test_gms_parent_grievance_submit.js",
        ],
        # 'web.assets_qweb': [
        #     '/openeducat_grievance_enterprise/static/src/xml/*.xml'
        # ],
        'web.assets_frontend': [
            "/openeducat_grievance_enterprise/static/src/js/custom.js",
            "/openeducat_grievance_enterprise/static/src/xml/*.xml"
        ],
        'web.assets_backend': [
            "/openeducat_grievance_enterprise/static/src"
            "/scss/common_style.scss"
        ],
    },
    'qweb': [],
    'images': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'Other proprietary',
    'live_test_url': 'https://www.openeducat.org/plans'
}
