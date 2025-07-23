# -*coding: utf-8 -*-
{
    "name": "ISEP - Document Pubic Portal",
    "summary": "Añade documentos publicos al portal del estudiante",
    "version": "16.0.1",
    "description": """
        Añade documentos publicos al portal del estudiante
    """,    
    "author": "HFoc",
    "maintainer": "HFoc",
    "images": ["images/isep_documents_portal.png"],
    "category": "Tools",
    "depends": [
        "base",
        "mail",
        "portal",
        "openeducat_core"
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/documents_folder_data.xml",
        "views/folders_views.xml",                  
        "views/documents_portal_templates.xml",         
        "views/menu.xml",   
    ],

    "installable": True
}
