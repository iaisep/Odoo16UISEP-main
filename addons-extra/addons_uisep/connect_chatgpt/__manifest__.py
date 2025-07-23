# -*- coding: utf-8 -*-
#--------------# 
#pip install beautifulsoup4
#pip install openai==0.28
{
    'name' : "Conector ChatGPT IA helpdesk",
    'summary': "conector ChatGPT con ia entrenada ISEP",
    'autor': "Rafael Valencia",
    "version": "16.0.4.2",
    'sequence': 101,
    'depends':['base','base_setup','helpdesk','knowledge','website_slides'],
    'data':[
        'security/ir.model.access.csv',
        'data/parser_config_data.xml',
        'data/config_despe_data.xml',
        'data/config_embeding_data.xml',
        'data/email_ia.xml',
        'data/cron_close_ticket.xml',
        'views/help_desk_ticket_view.xml',
        'views/mail_menssage_view.xml',
        'views/knowledge_article_view.xml',
        'views/helpdesk_team.xml',
        'views/mail_parser_config_view.xml',
        'views/model_config_consul_view.xml',
        'views/slide_slide_view.xml',
    ],
    'external_dependencies' : {
        'python' : ['beautifulsoup4','openai==0.28','python-docx','PyMuPDF','numpy','tiktoken'],
    },
    'demo':[],
    'qweb':[],
    'application':True,
    'installable':True,
    'auto_install':False,
}