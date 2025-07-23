# -*- coding: utf-8 -*-
{
    'name': 'Isep - eLearning with Bunny',
    'version': '16.0.1',
    'sequence': 10,
    'summary': 'Manage and publish an eLearning platform',
    'author': 'Hans Franco Olivos Cerna',
    'category': 'Website/eLearning',
    'description': """
        Create Online Courses Using Bunny
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
            'isep_bunny_elearning/static/src/xml/website_slides_fullscreen.xml',
            'isep_bunny_elearning/static/src/js/slides_course_fullscreen_player.js',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'AGPL-3',
}
