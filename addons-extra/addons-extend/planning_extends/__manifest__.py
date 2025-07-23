# -*- coding: utf-8 -*-
{
    'name': "Planning Extends - Planning Slot",

    'summary': """
        Módulo que extiende el objeto planning slot
        """,

    'description': """
       Módulo que extiende el objeto planning slot
    """,

    'author': "Breithner Aquituari",

    'category': 'Planning',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'project_forecast', 'sale_planning'],

    # always loaded
    'data': [
        'views/planning_slot.xml',
    ],
}
