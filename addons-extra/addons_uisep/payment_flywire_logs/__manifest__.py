# -*- coding: utf-8 -*-
#-------  -------# 
{   
    'name' : "Flywire LOGS",
    'summary': "verificacion de envios de flywire",
    'author': "William Valencia",
    'maintainer': 'ISEP',
    "version": "1.0.0",
    'category': 'Report',
    'sequence': 200,
    'depends':['base','base_setup','payment_flywire'],
    'data':[
        'security/ir.model.access.csv',
        'views/flyware_payload_log_view.xml',
    ],
    'demo':[],
    'qweb':[],
    'application':True,
    'installable':True,
    'auto_install':False,
}