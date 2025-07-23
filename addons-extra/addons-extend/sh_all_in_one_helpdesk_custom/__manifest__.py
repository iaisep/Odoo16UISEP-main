# Copyright 2014 ABF OSIELL <http://osiell.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


{
    "name": "Helpdesk_Tickets",
    "version": "16.0.1.1.1",
    "category": "Tools",
    "author": "ABF OSIELL, Odoo Community Association ()",
    "license": "LGPL-3",
    "development_status": "Production/Stable",
    "maintainers": [],
    "website": "Custom",
    "depends": ["sh_all_in_one_helpdesk"],
    "data": [
        "security/ir.model.access.csv",
        "template/template_helpdesk.xml",
        "views/category.xml",
        "views/sh_helpdesk_ticket_black_list_view.xml"
    ],
    "installable": True,
}
