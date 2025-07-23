# -*- coding: utf-8 -*-
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Isep Subject Precedence',
    'summary': """Isep Subject Precedence""",
    'description': """
    - Isep Subject Precedence
    """,
    'version': '1.4',
    'author': 'silvau',
    'category': 'Tools',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'web',
        'portal',
        'account',
        'openeducat_core',
        'openeducat_admission',
        'isep_documents_portal',
        'isep_website_custom',
        'isep_elearning_custom',
        'website_slides',
    ],
    'installable': True,
    'data': [
        'views/op_admission_view.xml',
        'views/op_course_view.xml',
        'views/op_subject_view.xml',
        'views/user_profile_content_details.xml',
        'wizard/subject_wizard.xml',
    ]
}
