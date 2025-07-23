# -*- coding: utf-8 -*-
{
    'name': 'ISEP - Public Content Slides JSON TXT',
    'version': '1.0',
    'author': "Hans Franco Olivos Cerna",
    'website': "https://app.universidadisep.com",
    'summary': 'Public Content Slides JSON TXT',
    'depends': ['website_slides','openeducat_core'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron_data.xml',
        'views/op_course.xml',
        #'views/op_subject.xml',
        'views/slide_channel.xml',

        
    ],
    'external_dependencies': {
        'python': ['beautifulsoup4','pymupdf'],
    },
    'installable': True,
    'application': False,
}

