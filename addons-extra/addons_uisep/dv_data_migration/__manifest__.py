# Personalizacion hecha para exportar los datos que se han hecho e importarla para no perderla WillVal117
{
    'name': 'Migracion DB Odoo - IA',
    'version': '1.0.3',
    'category': 'Tools',
    'summary': 'Tool for migrating',
    'description': """
""",
    'depends': ['base','base_setup','mail'],
    'support': '',
    'demo': [],
    'author': '',
    'website': '',
    'data': [
        'security/ir.model.access.csv',
        'data/data_config_instr.xml',
        'data/data_config_open.xml',
        'data/dv_data.xml',
        'views/dv_data_source_view.xml',
        'views/dv_data_target_view.xml',
        'views/dv_import_data_target_view.xml',
        'views/n_hub_migration_menus.xml',   
        'views/dv_data_openia_view.xml', 
    ],
    'external_dependencies': {
        'python': ['psycopg2'],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
