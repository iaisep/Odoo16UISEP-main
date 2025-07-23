# -*coding: utf-8 -*-
{
    "name": "Get books from student",
    "summary": "Automatically get books from student",
    "version": "16.1.1.0",
    "description": """
        
    """,    
    "author": "Eduardo",
    "maintainer": "Eduardo",
   
    "category": "Tools",
    "depends": [
        "base",
        "mail",
        "portal",
        "isep_gradebook",
        "openeducat_core",
        'survey'
    ],
    "data": [
       # "security/security.xml",
        #"security/ir.model.access.csv",
        'data/crono_get_books.xml',
        "views/webbookscomment.xml",   
        "views/send_to_book.xml", 
         
    ],
  

    "installable": True
}
