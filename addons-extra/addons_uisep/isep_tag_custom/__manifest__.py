# -*- coding: utf-8 -*-
#-------  -------# 
{   
    'name' : "Custom tag crm",
    'summary': "Custom tag crm",
    'author': "Universidad ISEP",
    'maintainer': 'William Valencia',
    "version": "1.0.1",
    'sequence': 200,
    'depends':['base','base_setup','sale','sales_team','contacts','crm','isep_student_migration','isep_res_partner_custom'],
    'data':[
        'data/data_tag_crm.xml',
        'views/crm_tag_view.xml',
        'views/crm_stage_view.xml',
        'views/product_template_view.xml',
        'views/op_course_type_view.xml',
    ],
    'demo':[],
    'qweb':[],
    'application':True,
    'installable':True,
    'auto_install':False,
}