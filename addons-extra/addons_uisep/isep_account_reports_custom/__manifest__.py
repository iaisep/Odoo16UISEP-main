# -*- coding: utf-8 -*-
#-------  -------# 
{   
    'name' : "Custom Accounting Reports",
    'summary': "Accounting Reports personalizacion",
    'author': "Universidad ISEP",
    'category': 'Accounting/Accounting',
    'website': '',
    'support': 'William Valencia', 
    "version": "1.0.1",
    'sequence': 200,
    'depends':['base','base_setup','account_accountant','account_reports'],
    'data':[
       'views/aged_partner_balance_view.xml',
    ],
    'demo':[],
    'qweb':[],
    'application':True,
    'installable':True,
    'auto_install':False,
}