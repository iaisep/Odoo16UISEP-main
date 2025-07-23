# -*- coding: utf-8 -*-
{
    "name": "Security User Roles",
    "version": "16.0.1.0.5",
    "category": "Extra Tools",
    "author": "faOtools",
    "website": "https://faotools.com/apps/16.0/security-user-roles-734",
    "license": "Other proprietary",
    "application": True,
    "installable": True,
    "auto_install": False,
    "depends": [
        "base"
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/data.xml",
        "data/cron.xml",
        "views/res_users.xml",
        "views/security_role.xml"
    ],
    "assets": {},
    "demo": [
        
    ],
    "external_dependencies": {},
    "summary": "The tool combines users in roles and simplifies security group assigning. Access group management. Users mass updating. Access groups management. Access organizational structure. Odoo user rights. Access rights. User security roles",
    "description": """For the full details look at static/description/index.html
* Features * 
- Temporary user blocking and activation
#odootools_proprietary""",
    "images": [
        "static/description/main.png"
    ],
    "price": "36.0",
    "currency": "EUR",
    "post_init_hook": "post_init_hook",
    "live_test_url": "https://faotools.com/my/tickets/newticket?&url_app_id=99&ticket_version=16.0&url_type_id=3",
}