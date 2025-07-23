# -*- coding: utf-8 -*-


{
    'name': 'Lead Assing Generation',
    'summary':  'Leads/Opportunities Assing',
    'category': 'Sales/CRM',
    'version': '1.2',
    'depends': [
      'crm'
    ],
    'data': [
       'views/crm_list_button.xml',
       'data/crono_assign.xml'
    ],
    
    'assets': {
        'web.assets_backend': [           
            '/isep_crm_asiguser/static/src/js/crm_tree_extend.js',           
            '/isep_crm_asiguser/static/src/xml/crm_list_button.xml',            
        ],
    },
    'license': 'LGPL-3',
}
