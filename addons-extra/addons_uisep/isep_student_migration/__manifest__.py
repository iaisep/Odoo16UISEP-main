# -*- coding: utf-8 -*-

{
    'name': 'student_migration',
    'summary': 'Módulo para la migración de estudiantes.',
    'description': 'Módulo para la migración de estudiantes, cursos, lotes, admisiones, etc.',
    'author': 'Contreras Pumamango Gianmarco - gmcontrpuma@gmail.com',
    'website': 'https://github.com/CodigoByte2020',
    'category': 'Tools',
    'version': '16.0.0.0.1',
    'depends': [
        'openeducat_core',
        'isep_elearning_custom',
        'openeducat_core_enterprise'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/op_area_course_views.xml',
        'views/op_course_type_views.xml',
        'views/op_course_views.xml',
        'views/op_modality_views.xml',
        'views/op_campus_views.xml',
        # 'views/op_practices_type_views.xml',
        'views/op_batch_views.xml'
    ],
    'installable': True,
}
