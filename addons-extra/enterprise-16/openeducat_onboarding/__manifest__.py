{
    'name': "OpenEduCat Onboarding",
    'summary': """OpenEduCat Onboarding""",
    'author': "OpenEduCat Inc",
    'website': "http://www.openeducat.org",
    'category': 'Tool',
    'version': '16.0.1.0',
    'license': 'Other proprietary',
    'depends': ['base','openeducat_core'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'views/onboarding_plan.xml',
        'views/onboarding_steps.xml',
        'data/onboarding_plan.xml',
        'data/menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            '/openeducat_onboarding/static/src/scss/style.scss',
            '/openeducat_onboarding/static/src/scss/jquery.fancybox.css',
            '/openeducat_onboarding/static/src/js/jquery.fancybox.js',
            '/openeducat_onboarding/static/src/js/header.js',
            '/openeducat_onboarding/static/src/xml/renderer.xml',
        ],
    },
    'auto_install': False,
    'application': True,
    # 'price': '199',
    # 'currency': 'EUR',

}
