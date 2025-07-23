{
    "name": "ISEP - Checklist of CRM Lead",
    'version': "16.0",
    'category': "CRM",
    "summary": "Seguimiento de leads",
    'author': 'HFoc',
    "depends": ['crm'],
    "data": [
        "security/ir.model.access.csv",
        "views/crm_lead_form.xml",
        "views/crm_checklist_view.xml",
        
    ],
    'images': ['static/description/banner.png'],
    'license': "OPL-1",
    'installable': True,
    'application': True,
    'auto_install': False,
}
