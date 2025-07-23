# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################


{
    'name': "OpenEduCat LMS Admission",
    'summary': """This module allows you to manage admission process
    efficiently in LMS courses.""",
    'version': '16.0.1.0',
    'category': 'Education',
    "sequence": 3,
    'complexity': "easy",
    'author': 'OpenEduCat Inc',
    'website': 'http://www.openeducat.org',
    'depends': [
        'openeducat_lms',
        'openeducat_admission_enterprise',
    ],
    'data': [
        'views/course_view.xml',
    ],
    'demo': [],
    'license': 'Other proprietary',
}
