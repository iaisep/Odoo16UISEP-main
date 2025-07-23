# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

{
    'name': 'OpenEduCat Assignment Grading Enterprise',
    'summary': """This module allows you to manage the assignments easily.
    Faculty can create assignment, publish it & student can make submission for that.
    After submission faulty can give grades to assignment""",
    'version': '16.0.1.0',
    'category': 'Education',
    "sequence": 3,
    'complexity': "easy",
    'author': 'OpenEduCat Inc',
    'website': 'http://www.openeducat.org',
    'depends': [
        'openeducat_assignment_enterprise'],
    'data': ['security/ir.model.access.csv',
             'views/grade_config_view.xml',
             'views/op_assignment_sub_line_view.xml',
             'views/grades_portal_view.xml',
             'menus/op_menu.xml'],
    'demo': ['demo/op_assign_grade_config.xml'],
    'images': [

    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'Other proprietary',
    'live_test_url': 'https://www.openeducat.org/plans'
}
