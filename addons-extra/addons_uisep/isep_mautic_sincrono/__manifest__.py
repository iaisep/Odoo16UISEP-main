
{
    'name': 'isep multi sincrono',
    'version': '6.0',
    'summary': 'Sincroniza cuando copia los leads a mautic y cuando los actualiza',
    'description': 'Determina cuando actualizar los leads en mautic y cuando crearlos',
    'category': 'Uncategorized',
    'author': 'Eduardo',
    'website': 'https://www.isep.com',
    'depends': ['base','crm'],
    'data': [
       # 'security/ir.model.access.csv',       
        'views/custom_crm_band.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'AGPL-3',
}
