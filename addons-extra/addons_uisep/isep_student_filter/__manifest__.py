# -*- coding: utf-8 -*-
{
    'name': 'Isep Student Filter Open-Educat',
    'version': '16.1',
    'summary': """ Modulo filtros al modulo de estudiantes y personalizaciones en la vista form """,
    'author': 'Breithner Aquituari',
    'website': '',
    'category': 'OpenEducat',
    'depends': [
                'base', 
                'isep_sign_sale',
                'openeducat_core', 
                'openeducat_admission', 
                ],
    "data": [
        "views/op_student_filter_views.xml"
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
