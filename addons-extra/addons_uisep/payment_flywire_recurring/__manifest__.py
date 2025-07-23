# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': "Payment Provider: Flywire recurring",
    'version': '1.0',
    'category': 'Accounting/Payment Providers',
    'sequence': 360,
    'summary': "Payment Provider: Flywire recurring",
    'description': "Payment Provider: Flywire recurring",
    'depends': ['payment_flywire','sale_subscription'],
    'data': [
        #'views/product_template.xml',
        #'views/payment_provider_views.xml',
        #'views/res_currency.xml',
    ],
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'license': 'LGPL-3',
}
