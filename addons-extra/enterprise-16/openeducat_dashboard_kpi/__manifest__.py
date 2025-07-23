# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

{
    "name": "OpenEducat Dashboard KPI",
    'summary': """Dashboard Pro is a Responsive Dashboard with customizable
    And Easy Configurable Item Settings. Dashboard Pro Helps You Make Eye On
    Your Important Data Easily. It Contains Multiple Tile View,
    Kpi View, List View, Multiple Chart View.""",
    "author": "OpenEduCat Inc",
    "sequence": 10,
    "installable": True,
    "auto_install": False,
    "website": "http://www.openeducat.org",
    "category": "Tools",
    "version": "16.0.1.0",
    "images": [],
    "depends": [
        "base",
        "web",
        "base_setup",
        "openeducat_admission",
        "openeducat_attendance",
        "openeducat_quiz",
        "openeducat_classroom_enterprise",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/dashboard_pro_security.xml",
        "data/default.xml",
        "views/dashboard_pro_theme_view.xml",
        "views/dashboard_pro_view.xml",
        "views/element_view.xml",
        "menus/menu.xml",
    ],
    'assets': {
        'web.assets_backend': [
            '/openeducat_dashboard_kpi/static/lib/css/gridstack.min.css',
            '/openeducat_dashboard_kpi/static/src/css/element.css',
            '/openeducat_dashboard_kpi/static/src/css/grid_configuration.css',
            '/openeducat_dashboard_kpi/static/src/css/main_dashboard.scss',
            '/openeducat_dashboard_kpi/static/lib/js/Chart.js',
            '/openeducat_dashboard_kpi/static/lib/js/Chart.min.js',
            '/openeducat_dashboard_kpi/static/lib/js/Chart.bundle.js',
            '/openeducat_dashboard_kpi/static/lib/js/Chart.bundle.min.js',
            '/openeducat_dashboard_kpi/static/src/js/formatting_function.js',
            '/openeducat_dashboard_kpi/static/src/js/date_widget.js',
            '/openeducat_dashboard_kpi/static/src/js/dashboard_pro.js',
            '/openeducat_dashboard_kpi/static/src/js/dashboard_pro_domain.js',
            '/openeducat_dashboard_kpi/static/src/js/components/*.js',
            '/openeducat_dashboard_kpi/static/src/xml/*.xml',
        ],
        'web.assets_qweb': [
            '/openeducat_dashboard_kpi/static/src/xml/*.xml'
        ],
    },
    "qweb": ["static/src/xml/*.xml"],
    "demo": ["demo/demo.xml", "demo/element_demo.xml"],
    "license": "Other proprietary",
}
