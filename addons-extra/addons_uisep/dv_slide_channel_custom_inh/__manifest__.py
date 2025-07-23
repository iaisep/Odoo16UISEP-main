# -*- coding: utf-8 -*-
{
    'name': 'IA-gpt Calificacion Cursos Extends',
    'version': '16.1',
    'summary': """ Módulo que por medio de una accion planificada, califica y envia a libreta """,
    'author': 'Breithner Aquituari',
    'website': '',
    'category': 'Elearning',
    'depends': ['base', 'dv_slide_channel_custom', 'isep_gradebook'],
    "data": [
        "data/cron_auto_send_library.xml",
        "views/survey_survey_views.xml"
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
