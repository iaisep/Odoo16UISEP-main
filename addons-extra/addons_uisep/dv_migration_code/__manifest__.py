# -*- coding: utf-8 -*-
#-------campos de soporte para migracion Hibrico 15 a 16  -------# 
{   
    'name' : "Campos para migracion",
    'summary': "Campos de apoyo para migracion",
    'author': "William Valencia",
    'maintainer': 'DEValencia',
    'website': 'https://github.com/Willval117',
    'support': 'Email --> willivalen19@gmail.com ', 
    "version": "1.0.0",
    'category': 'Tools',
    'sequence': 200,
    'depends':['base','base_setup','contacts', 'crm', 'sale_subscription', 'sale_temporal'],
    'data':[
        'views/dv_codeid_m_view.xml',
    ],
    'demo':[],
    'qweb':[],
    'application':True,
    'installable':True,
    'auto_install':False,
}