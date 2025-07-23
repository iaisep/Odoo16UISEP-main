{
    'name': "Isep - Sale subscription custom",
    'summary': """
        Sale subscription custom""",
    'description': """
        Sale subscription custom""",
    'author': "Hans Franco Olivos Cerna",
    'website': "https://universidadisep.com",
    'category': 'sale',
    'version': '16.0.2',
    'depends': ['base','sale_subscription','sales_team','account','sale','web','report_xlsx','web_grid','isep_openeducat_sale'],
    'images': ['static/description/icon.png'],
    'license': 'AGPL-3',
    'data': [
        'security/ir.model.access.csv',
        'data/cron.xml',
        'data/product_subscription_schedule.xml',
        'views/sale_order.xml',
        'views/product_product.xml',
        'views/sale_subscription_schedule.xml',
        'views/account_move.xml',
        'views/schedule_add_invoice_wizard.xml',
        'views/wizard_date_due.xml',
        'wizards/sale_order_datefilter_view.xml',
        'reports/report.xml',
        'reports/report_template_cartera.xml',
        'reports/report_template_estado_cuenta.xml',	
        
    ],
    'assets': {
        'web.assets_backend': [
            'isep_sale_subscription_custom/static/src/js/grid_controller.js',            
            'isep_sale_subscription_custom/static/src/css/grid_style.css',
        ],
    },
    'installable': True,
    'application': False,
}
