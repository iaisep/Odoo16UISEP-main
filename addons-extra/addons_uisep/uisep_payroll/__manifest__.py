# -*- coding: utf-8 -*-

{
    'name': "Hr Payroll UIsep",
    'version': "16.0.1.0",
    'author': 'Isep Latam S.C.',
    'website': 'https://www.isep.com',
    'depends': [
        "hr",
        "hr_contract",
        "hr_payroll",
        "hr_payroll_account",
        "nomina_cfdi_ee",
        "nomina_cfdi_extras_ee",
    ],
    "installable": True,
    "images":  [],
    'data': [
        'security/ir.model.access.csv',
        "views/hr_contract_views.xml",
        "views/hr_payslip_views.xml",
    ],
}
