# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name": "Login As Other User",

    "author": "Softhealer Technologies",

    "website": "https://www.softhealer.com",

    "support": "support@softhealer.com",

    "version": "16.0.1",

    "category": "Extra Tools",

    "summary": "Login As Another User Login As Impersonate User Login As Admin Users Login As Super User Login As Portal User Login Without ID Multiple Switch Users Access Odoo Without Login As Different User Odoo",

    "description": """This module allows special user to log in as other users and can access entire odoo same as other user accessing. Using this module you can switch to another user without login as well as help to switch in to the multiple users.""",

    "depends": ['base_setup'],

    "data": [
        'security/ir.model.access.csv',
        'security/sh_login_as_other_user_groups.xml',
        'wizard/sh_login_other_wizard_views.xml'
    ],
    "assets": {
        "web.assets_backend": [
            "sh_login_as_other_user/static/src/js/systray_icon_menu.js",
            'sh_login_as_other_user/static/src/xml/systray_menu.xml',
        ],
    },
    "installable": True,
    "auto_install": False,
    "application": True,
    "images": ["static/description/background.png", ],
    "license": "OPL-1",
    "price": "40",
    "currency": "EUR"
}
