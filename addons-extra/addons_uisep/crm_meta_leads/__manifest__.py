{
    'name': "CRM Meta Lead Ads",
    'summary': """
        Sincroniza Leads de Meta con el modulo de CRMSync Meta Leads with Odoo CRM""",
    'description': """
        Sincroniza Leads de Meta con el modulo de CRMSync Meta Leads with Odoo CRM""",
    'author': "HFoc - Hans Franco Olivos Cerna",
    'website': "https://universidadisep.com",
    'category': 'Lead Automation',
    'version': '16.0.1',

    'depends': ['crm'],
    'images': ['static/description/icon.png'],
    'license': 'AGPL-3',
    'data': [
        'data/ir_cron.xml',
        'data/crm.facebook.form.mapping.csv',
        'security/ir.model.access.csv',
        'views/crm_view.xml',
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
    'application': False,
}
