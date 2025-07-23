{
    'name': 'Isep - Documentos extended',
    'summary': 'Módulo de documentos extended.',
    'description': 'Módulo para la gestión de documentos extended.',
    'author': 'HFoc',
    'website': 'https://universidadisep.com',
    'category': 'Tools',
    'version': '16.0.0.0.2',
    'depends': [
        'isep_record_request',
        'openeducat_core',
        'openeducat_admission',
    ],
    'data': [
        'views/res_partner_views.xml',
        'views/op_student_views.xml',
        'views/op_admission_views.xml',
    ],
    'installable': True,
}
