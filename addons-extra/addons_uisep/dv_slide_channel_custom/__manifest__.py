# -*- coding: utf-8 -*-
#-------  -------# 
{   
    'name' : "IA-gpt Calificacion Cursos",
    'summary': "Autocalificacion con IA en cursos, contenido de certificaciones",
    'author': "William Valencia",
    'maintainer': 'DEValencia',
    'website': 'https://github.com/Willval117',
    'support': 'Email --> willivalen19@gmail.com ', 
    "version": "1.0.3",
    'category': 'eLearning',
    'sequence': 200,
    'depends':['base','base_setup','website_slides','survey','isep_survey'],
    'data':[
        'security/ir.model.access.csv',
        'views/dv_config_ia_view.xml',
        'views/dv_survey_survey_view.xml',
        'views/dv_survey_user_input_view.xml',
        'data/data_config_ia.xml',
        'data/cron_auto_score_ia.xml'
    ],
    'external_dependencies' : {
        'python' : ['beautifulsoup4','pandas','openai','python-docx','PyMuPDF','numpy','tiktoken','openpyxl'],
    },
    'demo':[],
    'qweb':[],
    'application':True,
    'installable':True,
    'auto_install':False,
}