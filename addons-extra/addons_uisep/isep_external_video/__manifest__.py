# -*- coding: utf-8 -*-
{
    'name': 'Isep - eLearning External video',
    'version': '16.0.1',
    'sequence': 10,
    'summary': 'Manage and publish an eLearning platform',
    'author': 'Hans Franco Olivos Cerna',
    'category': 'Website/eLearning',
    'description': """
        Create Online Courses Using video
    """,
    'depends': [
        'website_slides',
    ],
    'data': [
        'views/slide_slide_views.xml',
        'views/templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'isep_external_video/static/src/xml/website_slides_fullscreen.xml',
            'isep_external_video/static/src/js/slides_course_fullscreen_player.js',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'AGPL-3',
}


# https://isep.video/multimidias/mexico/videoclases/maestrias/psicologia/mtmp/mtmp_m01_u01_p02-03_tap.mp4