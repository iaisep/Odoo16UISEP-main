# -*- coding: utf-8 -*-
{
    'name': "Website slides customizations",
    'summary': "Module for extend website slides features",
    'description': """
    """,
    'author': "Mario A. Millet",
    'website': "",

    'category': 'Uncategorized',
    'version': '0.1',
    'license': 'LGPL-3',

    'depends': ['base',  'website_slides'],

    'data': [
        'views/slides.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'website_slides_customizations/static/src/frontend/jspdf.js',
            'website_slides_customizations/static/src/frontend/html2canvas.js',
            'website_slides_customizations/static/src/frontend/html2pdf.js',
            'website_slides_customizations/static/src/frontend/download.js',
        ],
    },
}
