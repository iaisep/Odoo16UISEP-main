# -*- coding: utf-8 -*-
{
    'name': "ISEP - Contacs custom",  
    'summary': """
        tag_custom: Etiqueta en Contacto tipo Char.
    """,
    'description': """
        Contacts custom
    """,
    'author': "HFoc", 
    'website': "https://universidadisep.com/",
    'category': 'Tools',
    'version': '16.0.1.0.0',
    'depends': ['base','contacts'],
    'data': [        
        'security/ir.model.access.csv',
        'views/res_partner_view.xml',   # Archivo de vistas
        'views/res_partner_tags_view.xml',  # Archivo de vistas para etiquetas
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}