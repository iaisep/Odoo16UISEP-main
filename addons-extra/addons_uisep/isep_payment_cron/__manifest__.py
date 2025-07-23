
{
    'name': 'Isep - Payments Cron',
    'version': '7.0',
    'summary': 'Realizar cobros de clientes tokenizados mediante cron',
    'description': """
        Esta función procesa los pagos de facturas publicadas que aún están pendientes de pago.
        Se enfoca en el modelo 'account.move' y selecciona facturas en estado 'posted'
        que no han sido pagadas. Utiliza un método de pago tokenizado, como Stripe, 
        guardado en la cuenta del cliente.
    """,
    'category': 'sale',
    'author': 'HFoc',
    'website': 'https://www.universidadisep.com',
    'depends': ['sale_subscription','base_automation_webhook','base_automation'],
    'data': [
        'data/cron.xml',
        'data/template_email_transac.xml',
        'views/account_move.xml',
        'views/sale_order_stage.xml',        
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
