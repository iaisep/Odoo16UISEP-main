# -*- coding: utf-8 -*-
{
    'name': "ISEP: Sign custom",
    'summary': "ISEP: Sign custom",
    'description': "ISEP: Sign custom",
    'author': "HFoc",
    'category': 'Tools',
    'version': '16.0',
    'depends': ['web'],
    'data': [
    ],
    'assets': {
        'web.assets_frontend': [
            'isep_sign_custom/static/src/js/name_and_signature_patch.js',
            'isep_sign_custom/static/src/xml/name_and_signature.xml',
            'isep_sign_custom/static/src/xml/name_and_signature_legacy.xml',
        ],
        'web.assets_common': [
            'isep_sign_custom/static/src/js/name_and_signature_patch.js',
            'isep_sign_custom/static/src/xml/name_and_signature_legacy.xml',
        ],
    },
    'license': 'LGPL-3',
    'installable': True,
    'application': True
}
