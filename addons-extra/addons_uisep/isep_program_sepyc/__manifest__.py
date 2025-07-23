# -*- coding: utf-8 -*-
{
    'name': 'Isep Program Sepyc',
    'version': '16.1',
    'summary': """ Módulo que permite activar desde el lote el programa Sepyc """,
    'author': 'Breithner Aquituari',
    'website': '',
    'category': '',
    'depends': [
        'base',
        'openeducat_admission', 
        'isep_student_migration', 
        'isep_student_filter',
        'isep_form_data' 
        
        ],
    "data": [
        "views/op_student_views.xml",
        "views/op_admission_views.xml",
        "views/res_partner_views.xml"
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
