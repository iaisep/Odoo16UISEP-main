# -*- coding: utf-8 -*-
{
    'name': 'Isep Op Sessions',
    'version': '16.1',
    'summary': """ Módulo para planificar sesiones de manera masiva """,
    'author': 'Breithner Aquituari',
    'website': '',
    'category': '',
    'depends': ['base','openeducat_lesson', 'openeducat_timetable','isep_elearning_custom'],
    "data": [
        "security/ir.model.access.csv",
        "wizard/op_session_wizard.xml",
        "views/op_session_views.xml"
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
