# -*- coding: utf-8 -*-

{
    'name': 'Extensión ADD',
    'version': '16.02',
    'description': ''' 
                    Agrega campos adicionales para extraer información de los XML's
                    ''',
    'category': 'Accounting',
    'author': 'IT Admin',
    'website': 'www.itadmin.com.mx',
    'depends': [
        'l10n_mx_sat_sync_itadmin_ee',
    ],
    'data': [
        'views/ir_attachment_view.xml',
    ],
    'assets': {
    },
    'application': False,
    'installable': True,
    'license': 'OPL-1',
}
