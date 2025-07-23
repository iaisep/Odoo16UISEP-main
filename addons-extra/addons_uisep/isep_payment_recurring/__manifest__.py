# -*- coding: utf-8 -*-
{
    'name': 'Isep_payment_recurring',
    'version': '16.1',
    'description': """ Isep_payment_recurring Description """,
    'summary': """ Isep_payment_recurring Summary """,
    'author': '',
    'website': '',
    'category': '',
    'depends': ['base','account' ],
    "data": [
        "security/ir.model.access.csv",
        "views/website_form.xml",
        "views/account_move_views.xml",
        "wizard/form_view.xml",
        "views/data_flywire_views.xml",
        "views/flywire_notification_views.xml"
    ],
    'assets': {
        'web.assets_frontend': [
            '/isep_payment_recurring/static/src/scss/form.scss',
            '/isep_payment_recurring/static/src/js/flywire_event.js',
        ],
    },

    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}



    # 'assets': {
    #     'web.assets_backend': [
    #         '/isep_record_request/static/src/xml/ir_attachment_preview.xml',
    #         '/isep_record_request/static/src/js/ir_attachment_preview.js'
    #     ]
    # }
