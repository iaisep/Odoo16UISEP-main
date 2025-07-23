# -*- coding: utf-8 -*-
{
    'name': 'ISEP Tesis modelo',
    'version': '1.0.0',
    'summary': """ modulo y portal para revision de tesis pensado para usarse con IA usando webhooks""",
    'description': """ modulo y portal para revision de tesis pensado para usarse con IA usando webhooks""",
    'author': 'Isep Latam, SC / William Valencia.',
    'website': '',
    'category': 'Education',
    'depends': [
        'base',
        'mail',
        'portal',
        'openeducat_core',
        'openeducat_fees',
        'openeducat_admission',
        'website',
        'sign',
        'base_location',
        'base_location_geonames_import'
    ],
    "data": [
        "security/ir.model.access.csv",

        "views/menu_views.xml",

        "views/tesis_model_views.xml",


        "templates/portal_my_tesis_model.xml",
        "templates/tesis_model_form_template.xml",
        "templates/tesis_model_portal_template.xml",
        "templates/tesis_model_portal_details_template.xml",
  

    ],

    'assets': {
    },
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
