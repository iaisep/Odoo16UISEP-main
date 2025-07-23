# -*- coding: utf-8 -*-
{
    'name': 'Isep - eLearning with Scorm',
    'version': '16.0.1',
    'sequence': 10,
    'summary': 'Manage and publish an eLearning platform',
    'author': 'Hans Franco Olivos Cerna',
    'category': 'Website/eLearning',
    'description': """
        Create Online Courses Using Scorm
    """,
    'depends': [
        'website_slides',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/slide_slide_views.xml',
        'views/templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'isep_scorm_elearning/static/src/xml/website_slides_fullscreen.xml',
            'isep_scorm_elearning/static/src/js/slides_course.js',
            'isep_scorm_elearning/static/src/js/slides_course_fullscreen_player.js',
        ],
    },
    'images': ["static/description/images/scorm_banner.png"],
    'installable': True,
    'application': True,
    'license': 'AGPL-3',
}
