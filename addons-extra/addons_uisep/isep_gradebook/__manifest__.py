{
    'name': "Isep - Openeducat Gradebook",
    'summary': """
        Gradebook de Isep para Openeducat""",
    'description': """
        Gradebook de Isep para Openeducat""",
    'author': "HFoc - Hans Franco Olivos Cerna",
    'website': "https://universidadisep.com",
    'category': 'Openeducat',
    'version': '16.0.1',
    'depends': ['website_slides','website_slides_forum','isep_elearning_custom','openeducat_core','openeducat_admission','openeducat_core_enterprise','survey','isep_survey'], # isep_website_custom
    'images': ['static/description/icon.png'],
    'license': 'AGPL-3',
    'data': [ 
        'security/res_groups.xml',
        'security/ir.model.access.csv', 
        'report/reports.xml',
        'report/recognition_certificate.xml',
        'data/cron_admission_summary.xml',
        'data/mail_recognition_certificate.xml',        
        'views/app_gradebook.xml',
        'views/gradebook_templates.xml',
        'views/op_course.xml',
        'views/op_subject.xml',        
        'views/survey_user_input.xml',
        'views/survey_question_write.xml',
        'views/app_gradebook_subject.xml',
        'views/app_gradebook_student.xml',
        'views/app_gradebook_pending.xml',
        'views/menu.xml',
        'views/app_gradebook_student_report.xml',
        'views/app_gradebook_summary_view.xml',

        
    ],    
    'installable': True,
    'application': False,
}
