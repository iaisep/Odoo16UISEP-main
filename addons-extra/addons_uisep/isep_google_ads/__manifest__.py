{
    'name': "Isep - Google Ads",
    'version': '1.0',
    'category': 'sale',
    'sequence': 1,
    'summary': "Webhook para Google Ads",
    "author": "HFoc - Hans Franco Olivos Cerna",
    'depends': ['sale','crm'],
    'data': [
        'security/ir.model.access.csv',
        'views/isep_google_forms.xml',
        'views/isep_google_leads.xml',
        'views/crm_lead.xml',        
        'views/menu.xml', 
    ],    
    'application': False,
    'installable': True,
    'license': 'LGPL-3',
}
