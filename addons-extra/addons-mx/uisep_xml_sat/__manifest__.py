# -*- coding: utf-8 -*-
{
    'name': "Descarga XML SAT",
    'version': '1.0',
    "summary":  """ Descarga de XML CFDI del portal del SAT """,
    'description': """
        Descargar los XLM CFDI's del portal del SAT.
    """,
    'author': '',
    'depends': ['base', 'product'],
    "installable": True,
    "images":  [],
    'data': [
        'security/ir.model.access.csv',
        'views/menuitem_views.xml',
        'views/company_views.xml',
        'views/xmlsat_views.xml',
        'data/scheduled_actions.xml'
    ],
    'external_dependencies': {"python": [
        'cfdiclient',
        'zipfile'
    ]},
    "application": True,
}
