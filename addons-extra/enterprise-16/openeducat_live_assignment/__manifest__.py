{
    'name': 'OpenEduCat Live Assignment',
    'summary': """This module allows you to manage the assignments easily. Faculty
    can create and allocate assignment,it & student can make submission for that.""",
    'version': '16.0.1.0',
    'category': 'Productivity/Discuss',
    'sequence': 145,
    'author': 'OpenEduCat Inc',
    'company': 'OpenEduCat Inc.',
    'depends': ['mail', 'openeducat_assignment_enterprise', 'openeducat_live'],
    'website': 'http://www.openeducat.org',
    'data': [
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'assets': {
        'web.assets_qweb': [
            'openeducat_live_assignment/static/src/xml/*.xml',
        ],
        'web.assets_backend': [
            'openeducat_live_assignment/static/src/js/*.js',
            'openeducat_live_assignment/static/src/xml/*.xml',
        ],
        'mail.assets_discuss_public': [
            'openeducat_live_assignment/static/src/js/*.js',
            'openeducat_live_assignment/static/src/xml/*.xml',
        ],
    },
    'license': 'Other proprietary',
}
