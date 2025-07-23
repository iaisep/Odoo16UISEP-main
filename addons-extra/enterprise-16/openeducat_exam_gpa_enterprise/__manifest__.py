# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

{
    'name': 'OpenEduCat Exam GPA Enterprise',
    'summary': """This module allows you to give credit points based on
    GPA(Grade Point Average) system.""",
    'version': '16.0.1.0',
    'category': 'Education',
    "sequence": 3,
    'complexity': "easy",
    'author': 'OpenEduCat Inc',
    'website': 'http://www.openeducat.org',
    'depends': [
        'openeducat_exam_enterprise',
        'openeducat_student_progress_enterprise',
    ],

    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'report/report_menu.xml',
        'report/student_progression_report.xml',
        'views/grade_points_view.xml',
        'views/student_progression_view.xml',
    ],
    'demo': [
        'demo/course_inherit.xml',
        'demo/grade_config.xml',
        'demo/result_template_inherit.xml',
    ],

    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'Other proprietary',
    'live_test_url': 'https://www.openeducat.org/plans'

}
