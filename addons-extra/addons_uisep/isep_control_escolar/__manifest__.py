# -*- coding: utf-8 -*-
{
    'name': "Isep Student Reports",
    'summary': "Isep - Student Reports",
    'description': "Isep - Student Reports",
    'author': "silvau",
    'category': 'website',
    'version': '1.2',
    'depends': ['base','openeducat_core_enterprise','isep_student_migration'],
    'data': [
        'security/ir.model.access.csv',
        'views/sep_report.xml',
        'views/student_report.xml',
        'views/op_student_view.xml',
        'views/op_admission_view.xml',
        'views/op_batch_view.xml',
        'views/op_course_view.xml',
        'views/sep_report_log_view.xml',
    ],
}
