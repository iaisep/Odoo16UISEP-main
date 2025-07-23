{
    'name': 'Duplicate Intercompany',
    'version': '1.2',
    'category': 'Account',
    'summary': 'Account internal machinery',
    'description': """
        This module contains all the common features of accounting.
    """,
    'depends': [
        "account",
    ],
    'data': [
        "security/ir.model.access.csv",
        "data/dablicate_intercompany_data.xml",
        "wizard/cambiar_factura_de_compania.xml",
    ],
    'demo': [],
    'installable': True,
    'license': 'LGPL-3',
}





