# -*coding: utf-8 -*-
{
    "name": "Automation of student documents by email",
    "summary": "Automation of student documents by email",
    "version": "16.1.2",
    "description": """
        
    """,    
    "author": "Eduardo",
    "maintainer": "Eduardo",
   
    "category": "Tools",
    "depends": [
        "base",
        "mail",
        "portal",
        "openeducat_core",
        "openeducat_admission"
    ],
    "data": [
       # "security/security.xml",
        #"security/ir.model.access.csv",        
        #  "data/next_date.xml",   
        # "data/validate_documents.xml",    
        "data/email_send_tempate_month1.xml",
        "data/email_send_tempate_month2.xml",
        "data/email_send_tempate_month3.xml",
        "data/email_send_tempate_month4.xml",
        "data/email_send_tempate_month5.xml",
        "data/email_send_template_success.xml",
        'data/autosend_template.xml',
        'data/complate_documents.xml',
        "views/op_confim_reception.xml",    
        "views/op_opcurse.xml", 
        
    ],

    "installable": True
}
