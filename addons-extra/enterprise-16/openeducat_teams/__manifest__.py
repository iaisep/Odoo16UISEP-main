# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

{
    'name': 'OpenEduCat Teams',
    'summary': """This module allows you to manage
    and create calender online meeting using session on Microsoft Teams.""",
    'version': '16.0.1.0',
    'category': 'Education',
    "sequence": 3,
    'complexity': "easy",
    'author': 'OpenEduCat Inc',
    'website': 'http://www.openeducat.org',

    'depends': ['openeducat_core_enterprise',
                'openeducat_online_tools_enterprise',
                'openeducat_timetable_enterprise',
                ],

    'data': [
        'security/ir.model.access.csv',
        'data/api_data.xml',
        'data/refresh_ir_cron.xml',
        'views/res_config_settings.xml',
        'views/token_view.xml',
        'wizard/teams_meeting_view.xml',
        'views/msteams_meeting_view.xml',
        'views/op_course.xml',
        'views/op_subject.xml',
        'views/online_meeting_template.xml',
    ],
    'demo': ['demo/faculty_demo.xml'],

    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'Other proprietary',
    'external_dependencies': {'python': ['pymsteams',
                                         'o365']},
    'live_test_url': 'https://www.openeducat.org/plans'

}
