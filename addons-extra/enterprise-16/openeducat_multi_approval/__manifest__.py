{
    'name': "OpenEduCat Approval All in One",
    'summary': """Approval All in One Management""",
    'author': "OpenEduCat Inc",
    'website': "http://www.openeducat.org",
    'category': 'Tool',
    'version': '16.0.1.0',
    'license': 'Other proprietary',
    'depends': ['base', 'product', 'mail', 'base_automation'],
    'data': [
        'security/approval_security.xml',
        'security/ir.model.access.csv',
        'data/mail_template.xml',
        'views/mail_activity_views.xml',
        'views/multi_approval_views.xml',
        'views/approval_model_request_views.xml',
        'views/approval_request_views.xml',

    ],
    'auto_install': False,
    'application': True,

}
