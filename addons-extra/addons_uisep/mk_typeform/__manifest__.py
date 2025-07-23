# -*- coding: utf-8 -*-
{
    'name': "Typeform Odoo Connector",
    "category": "Sales",
    "website": "https://universidadisep.com/",
    "author": "HFoc - Hans Franco Olivos Cerna",
    'version': '16.0.1',
    "license": "Other proprietary",
    'depends': ['crm','sales_team'],
    'data': [
        'security/ir.model.access.csv',
        'views/crm_typeform.xml',
        'views/form_model_relation.xml',
        'views/form_submit.xml',
        'views/menus.xml'
    ],    
    'summary': """Typeform Odoo Connector""",
    'description': """
        Modulo para la comunicacion con Typeform, recibe la informacion de los formularios enviado usando un webhook
    """,   
    "images": [
        "static/description/icon.png"
    ],
    'application': True,
    "installable": True,
}
