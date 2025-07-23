{
    'name': "Isep - Openeducat Custom",
    'summary': """
        Personalizaciones de Isep para Openeducat""",
    'description': """
        Personalizaciones de Isep para Openeducat""",
    'author': "HFoc - Hans Franco Olivos Cerna",
    'website': "https://universidadisep.com",
    'category': 'Openeducat',
    'version': '16.0.1',
    'depends': ['openeducat_core','openeducat_admission','openeducat_core_enterprise','openeducat_assignment_enterprise'],
    'images': ['static/description/icon.png'],
    'license': 'AGPL-3',
    'data': [
        'data/ir_cron_admission.xml',
        'views/op_admission_tree.xml',
        'views/op_batch.xml',
        'views/menus.xml',
        'views/op_assignment.xml',
        'views/op_assignment_sub_line.xml',
        'portal/assignment_marks_view.xml'
    ],    
    'installable': True,
    'application': False,
}
