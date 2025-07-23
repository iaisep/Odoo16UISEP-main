# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

{
    'name': 'OpenEduCat Job Skill Bridge',
    'version': '16.0.1.0',
    'category': 'Education',
    "sequence": 3,
    'complexity': "easy",
    'author': 'OpenEduCat Inc',
    'website': 'http://www.openeducat.org',
    'depends': [
        'openeducat_core_enterprise',
        'openeducat_placement_job_enterprise',
        'openeducat_skill_enterprise',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/job_post_view_inherit.xml',
        'views/openeducat_add_skill_portal.xml',
        'views/openeducat_student_skill_portal.xml',
        'views/skill_line_view.xml',
        'views/student_view.xml',
    ],
    'qweb': [],
    'demo': [
        'demo/skill_line_demo.xml',
        'demo/job_post_demo.xml'
    ],
    'images': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'Other proprietary',
}
