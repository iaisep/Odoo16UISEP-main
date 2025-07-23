# -*- coding: utf-8 -*-
{
    'name': "Comisión por Mensualidades Affiliate Manager",

    'summary': """
        Modificaciones al modulo affiliate_management para incluir comisiones por mensualidad""",

    'description': """
        Modificaciones al modulo affiliate_management para incluir comisiones por mensualidad
    """,

    'author': "JPHA",
    'category': 'Website',
    'version': '0.1',


    'depends': ['base', 'affiliate_management'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/views_res_partner.xml',
        'views/view_product_template.xml',
        'views/views_res_config_setting.xml',
        'views/views_affiliate_management.xml'
    ],

    'demo': [
        'demo/demo.xml',
    ],
}
