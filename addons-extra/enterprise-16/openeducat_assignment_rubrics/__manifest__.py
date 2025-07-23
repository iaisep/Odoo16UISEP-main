# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

{
    'name': 'OpenEduCat Assignment Rubrics Enterprise',
    'summary': """This module allows Faculty to Create Rubrics Template to grade
    the assignments based on points or percentage and manage the
    assignment submission.""",
    'version': '16.0.1.0',
    'category': 'Education',
    "sequence": 3,
    'complexity': "easy",
    'author': 'OpenEduCat Inc',
    'website': 'http://www.openeducat.org',
    'depends': ['openeducat_assignment_enterprise',
                'mail'],
    'data': ['security/ir.model.access.csv',
             'views/rubrics_element_view.xml',
             'views/rubrics_template_view.xml',
             'views/op_assignment_view_inherit.xml',
             'views/op_assignment_sub_line_view_inherit.xml',
             'views/op_assignment_sub_rubrics_view.xml',
             'menus/op_menu.xml'],
    'demo': ['demo/rubrics_template_demo.xml',
             'demo/rubrics_element_demo.xml',
             'demo/op_assignment_demo.xml',
             'demo/op_assignment_rubric_sub_line_demo.xml',
             'demo/op_assignment_sub_line.xml'],
    'images': [],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'Other proprietary',
    'live_test_url': 'https://www.openeducat.org/plans'
}
