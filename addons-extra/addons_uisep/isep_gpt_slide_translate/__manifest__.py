# -*- coding: utf-8 -*-
{
    'name': 'Isep - Traduccion de contenido en Elearning',
    'version': '16.0.1.1.2',
    'license': 'AGPL-3',
    'summary': 'Traduccion de contenido en Elearning',
    'description': 'Traduccion de contenido en Elearning',
    'author': 'Hans Franco Olivos Cerna',
    'company': 'Universidad Isep',
    'maintainer': 'HFoc',
    'website': 'https://universidadisep.com',
    'depends': ['website_slides','chatgpt_base'],
    'data': [
        'security/ir.model.access.csv',
        'data/gpt_data.xml',
        'views/slide_slide.xml',
        'views/wizard_slide_translate.xml',
    ],
    'external_dependencies': {'python': ['openai','tiktoken']},
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
}
