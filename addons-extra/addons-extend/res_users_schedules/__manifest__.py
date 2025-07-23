# -*- coding: utf-8 -*-
{
    'name': "Res Users Schedules",

    'summary': """
        Módulo que extiende el objeto usuario para sus horarios
        """,

    'description': """
       Módulo que extiende el objeto usuario para sus horarios
    """,

    'author': "Breithner Aquituari",

    'category': 'Users',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','whatsapp_connector'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/schedules.xml',
    ],
}
