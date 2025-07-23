# -*- coding: utf-8 -*-
{
    'name': "Report certificate others",

    'summary': """
        crear reportes de certificacion""",

    'description': """
        crear reportes de certificacion
    """,

    'author': "Eduardo Alejandro",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '16.1.0.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base','survey'],

    # always loaded
    'data': [
        #'security/ir.model.access.csv',        
       'views/report_certificate_latam.xml',    
       'views/report_paperformat.xml',
       'views/certificate_config.xml',
   
      

   
    ],
    
}
