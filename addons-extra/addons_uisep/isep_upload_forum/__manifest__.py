# -*- coding: utf-8 -*-
{
    'name': 'Isep Upload Post Forum',
    'version': '16.1',
    'summary': """ Modulo para cargar foros por archivo CSV """,
    'author': 'Breithner Aquituari',
    'website': '',
    'category': 'Website',
    'depends': ['base','website_forum','website_slides_forum','web' ],
    "data": [
        "wizard/forum_csv_import_wizard.xml",
        "security/ir.model.access.csv",
        "views/forum_forum_views.xml"
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
