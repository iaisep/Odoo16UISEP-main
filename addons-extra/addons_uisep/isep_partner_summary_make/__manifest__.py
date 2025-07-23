# -*- coding: utf-8 -*-
{
    'name': 'Isep Call Summary Contact',
    'version': '16.1',
    'summary': """ Módulo que permite almacenar los resúmenes de las llamadas del res.partner """,
    'author': 'Breithner Aquituari',
    'website': '',
    'category': '',
    'depends': ['base', 'crm', 'hr'],
    "data": [
        "security/ir.model.access.csv",
        "views/res_partner_views.xml",
        "views/crm_lead_views.xml",
        "views/hr_employee_views.xml"
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
