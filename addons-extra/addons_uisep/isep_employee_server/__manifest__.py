# -*- coding: utf-8 -*-
{
    'name': 'Isep Formatos de Impresión',
    'version': '1.0',
    'summary': """ Módulo de formato de impresión en el modelo hr.employee """,
    'author': 'Breithner Aquituari',
    'website': '',
    'category': '',
    'depends': ['base','hr_contract_sign', 'hr'],
    "data": [
        "reports/hr_employee_report_datos.xml",
        "reports/hr_emplyee_report_freelance.xml",
        "reports/hr_emplyee_report_reglamento.xml",
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}