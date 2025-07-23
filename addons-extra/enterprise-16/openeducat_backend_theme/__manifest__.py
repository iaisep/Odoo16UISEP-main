# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

{

    "name": "OpenEduCat Backend Theme",
    'summary': """This module adds the feature of beautiful enterprise theme look
 to OpenEduCat. And good usability.""",
    "category": "Tools",
    "version": "16.0.1.0",
    'author': 'OpenEduCat Inc',
    'website': 'http://www.openeducat.org',
    'company': 'OpenEduCat Inc.',
    "depends": ['base', 'web'],

    "data": [
        'views/style.xml',
        'data/theme_config.xml',
        'views/sidebar.xml',
        'views/web.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'openeducat_backend_theme/static/src/scss/login.scss',
        ],
        'web.assets_backend_prod_only': [
            ('replace', 'web/static/src/main.js',
             'openeducat_backend_theme/static/src/js/edu/starter.js'
             ),
        ],
        'web.assets_backend': [
            'openeducat_backend_theme/static/src/scss/theme_primary_variables.scss',
            'openeducat_backend_theme/static/src/scss/edu/apps_menu.scss',
            'openeducat_backend_theme/static/src/scss/edu/common_style.scss',
            'openeducat_backend_theme/static/src/scss/edu/fields_extra.scss',
            'openeducat_backend_theme/static/src/scss/edu/form_view_extra.scss',
            'openeducat_backend_theme/static/src/scss/edu/list_view_extra.scss',
            'openeducat_backend_theme/static/src/scss/edu/navbar.scss',
            'openeducat_backend_theme/static/src/scss/edu/search_view_extra.scss',
            'openeducat_backend_theme/static/src/scss/edu/webclient_extra.scss',
            'openeducat_backend_theme/static/src/scss/kanban_view_mobile.scss',
            'openeducat_backend_theme/static/src/scss/search_view_mobile.scss',
            'openeducat_backend_theme/static/src/scss/search_view_extra.scss',
            'openeducat_backend_theme/static/src/scss/backend_theme_customizer/dark_mode.scss',
            'openeducat_backend_theme/static/src/scss/backend_theme_customizer/style.scss',
            'openeducat_backend_theme/static/src/scss/sidebar.scss',
            'openeducat_backend_theme/static/src/scss/web_responsive.scss',
            'openeducat_backend_theme/static/src/js/edu/apps_menu.js',
            'openeducat_backend_theme/static/src/js/edu/web_client.js',
            'openeducat_backend_theme/static/src/js/edu/control_panel.js',
            'openeducat_backend_theme/static/src/js/edu/control_legacy_panel.js',
            'openeducat_backend_theme/static/src/js/edu/DropdownItem.js',
            'openeducat_backend_theme/static/src/js/edu/home_menu_wrapper.js',
            'openeducat_backend_theme/static/src/js/edu/home_menu.js',
            'openeducat_backend_theme/static/src/js/edu/search_panel.js',
            'openeducat_backend_theme/static/src/js/edu/user_menu.js',
            'openeducat_backend_theme/static/src/js/edu/field_upgrade.js',
            '/openeducat_backend_theme/static/src/js/sidebar.js',
            'openeducat_backend_theme/static/src/js/edu/backend_theme_customizer.js',
            'openeducat_backend_theme/static/lib/spectrum/js/spectrum.js',
            'openeducat_backend_theme/static/lib/jquery.touchSwipe/jquery.touchSwipe.js',
            'openeducat_backend_theme/static/src/xml/backend_theme_customizer.xml',
            'openeducat_backend_theme/static/src/xml/navbar.xml',
            'openeducat_backend_theme/static/src/xml/menu.xml',
            'openeducat_backend_theme/static/src/scss/theme_primary_variables.scss',
            'openeducat_backend_theme/static/lib/spectrum/css/spectrum.css',
            '/openeducat_backend_theme/static/src/scss/style.scss',
            'openeducat_backend_theme/static/src/scss/fonts.scss',
        ],
        'web.assets_qweb': [
            'openeducat_backend_theme/static/src/xml/menu.xml',
            'openeducat_backend_theme/static/src/xml/backend_theme_customizer.xml',
        ],

        'web._assets_bootstrap': [
            'openeducat_backend_theme/static/src/scss/theme_primary_variables.scss',
            'openeducat_backend_theme/static/src/scss/edu/form_view_extra.scss',
        ],

        'web._assets_helpers': [
            'openeducat_backend_theme/static/src/scss/variables.scss',
        ],

        'web._assets_primary_variables': [
            '/openeducat_backend_theme/static/src/scss/theme_primary_variables.scss',
            '/openeducat_backend_theme/static/src/scss/backend_theme_customizer/colors.scss',
        ],

    },
    'images': ['static/description/openeducat_backend_theme_banner.jpg'],
    'license': 'LGPL-3',
    'installable': False,
    'application': False,
    'pre_init_hook': '_backend_theme_pre_init',
    'auto_install': False,
    # ESTE MODULO FUE DISEÑADO PARA  ODOO COMMUNITY, NO SE DEBE INTENTAR INSTALAR EN ENTERPRISE!
}
