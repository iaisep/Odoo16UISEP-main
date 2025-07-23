# -*- coding: utf-8 -*-
{
    'name': 'ISEP - Knowledge Content Integration',
    'version': '1.0',
    'author': "Hans Franco Olivos Cerna",
    'website': "https://app.universidadisep.com",
    'summary': 'Sync slide content with Knowledge articles',
    'depends': ['knowledge', 'website_slides'],
    'data': [
        'data/ir_cron_data.xml',        
        # 'data/ir_config_parameter.xml',
        'views/slide_channel.xml',
    ],
    'external_dependencies': {
        'python': ['beautifulsoup4','pymupdf'],
    },
    'installable': True,
    'application': False,
}

