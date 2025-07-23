# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "Payment Provider: Flywire",
    'version': '1.0',
    'category': 'Accounting/Payment Providers',
    'sequence': 350,
    'summary': "Payment Provider: Flywire",
    'description': "Payment Provider: Flywire",
    'depends': ['payment','website'],
    'data': [
        'security/ir.model.access.csv',
        'views/payment_flywire_templates.xml',
        'views/payment_provider_views.xml',
        'views/product_template.xml',
        'views/res_currency.xml',
        'data/payment_provider_data.xml',
    ],
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'license': 'LGPL-3',
}
