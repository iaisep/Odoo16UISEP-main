# -*- coding: utf-8 -*-
{
    'name': 'ISEP Prácticas',
    'version': '16.1',
    'summary': """ Módulos de Prácticas Migrate""",
    'author': 'Isep Latam, SC / Breithner Aquituari',
    'website': '',
    'category': 'Education',
    'depends': [
        'base',
        'mail', 
        'portal', 
        'openeducat_core',
        'openeducat_fees', 
        'openeducat_admission',
        'website',
        'sign', 
        'base_location'
        ],
    "data": [
        "security/ir.model.access.csv",
        "reports/specific_agreement_report.xml",
        # "views/res_company_views.xml",
        "reports/framework_agreement_report.xml",
        "views/practice_practice.xml",
        "views/res_partner_center.xml",
        "views/practice_temary.xml",
        "views/practice_schedule.xml",
        "views/practice_center_course.xml",
        "views/practice_center_tutor.xml",
        "views/practice_schedule_days.xml",
        "views/practice_tutor_course.xml",
        "views/practice_type_form_assessment_tutor.xml",
        "views/practice_type_form_center.xml",
        "views/practice_type_form_completion_questionnaire.xml",
        "views/practice_type_form_internship_request.xml",
        "menu/isep_practices_menu.xml",
    ],

    'assets': {
        'web.report_assets_common': [
            '/isep_practices/static/src/css/format_report.css',
        ],
    },
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
