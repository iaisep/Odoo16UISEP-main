# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name": "All In One Helpdesk | CRM Helpdesk | Sale Order Helpdesk | Purchase Helpdesk | Invoice Helpdesk | Helpdesk Timesheet | Helpdesk Support Ticket To Task",
    "author": "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "category": "Discuss",
    "license": "OPL-1",
    "summary": "Flexible HelpDesk Customizable Help Desk Service Desk HelpDesk With Stages Help Desk Ticket Management Helpdesk Email Templates Email Alias Email Helpdesk Chatter Sale Order With Helpdesk,Purchase Order With Helpdesk Invoice With Helpdesk Apps for purchase Material Requisitions Request  purchase product Requisitions Request Material Requisition for tender Material Requisition for manufacturing order Product Request on RFQ Product Request on Tender Product Request on manufacturing order Odoo",
    "description": """Are you looking for fully flexible and customisable helpdesk in odoo? Our this apps almost contain everything you need for Service Desk, Technical Support Team, Issue Ticket System which include service request to be managed in Odoo backend. Support ticket will send by email to customer and admin. Customer can view their ticket from the website portal and easily see stage of the reported ticket. This desk is fully customizable clean and flexible. """,
    "version": "16.0.6",
    "depends": ["mail", "portal", "product", "resource", "sale_management", "purchase", "account", "hr_timesheet", "crm", "project", ],
    "data": [
        "security/sh_helpdesk_security.xml",
        "security/ir.model.access.csv",

        "data/sh_helpdesk_email_data.xml",
        "data/sh_helpdesk_data.xml",
        "data/sh_helpdesk_cron_data.xml",
        "data/sh_helpdesk_stage_data.xml",

        "views/sh_helpdesk_menu.xml",
        "views/sh_helpdesk_sla_policies.xml",
        "views/sh_helpdesk_alarm.xml",

        "data/sh_helpdesk_reminder_cron.xml",
        "data/sh_helpdesk_reminder_mail_template.xml",

        "views/sh_helpdesk_team_view.xml",
        "views/sh_helpdesk_ticket_type_view.xml",
        "views/sh_helpdesk_subject_type_view.xml",
        "views/sh_helpdesk_tags_view.xml",
        "views/sh_helpdesk_stages_view.xml",
        "views/sh_helpdesk_category_view.xml",
        "views/sh_helpdesk_subcategory_view.xml",
        "views/sh_helpdesk_priority_view.xml",
        "views/sh_helpdesk_config_settings_view.xml",
        "views/sh_helpdesk_ticket_view.xml",
        "views/sh_report_helpdesk_ticket_template.xml",
        "views/sh_helpdeks_report_portal.xml",
        "views/action_report_views.xml",
        "views/sh_ticket_feedback_template.xml",
        "views/sh_ticket_dashboard_templates.xml",
        "views/res_users.xml",
        "views/sh_helpdesk_merge_ticket_action.xml",
        "views/sh_helpdesk_ticket_multi_action_view.xml",
        "views/sh_helpdesk_ticket_update_wizard_view.xml",
        "views/sh_helpdesk_ticket_portal_template.xml",
        "views/sh_helpdesk_ticket_megre_wizard_view.xml",
        "views/sh_helpdesk_ticket_task_info.xml",

        "wizard/mail_compose_view.xml",

        "sh_helpdesk_so/security/sh_helpdesk_so_security.xml",
        "sh_helpdesk_so/views/sh_helpdesk_so_tickets.xml",

        "sh_helpdesk_po/security/sh_helpdesk_po_security.xml",
        "sh_helpdesk_po/views/sh_helpdesk_po_tickets.xml",

        "sh_helpdesk_invoice/security/sh_helpdesk_invoice_security.xml",
        "sh_helpdesk_invoice/views/sh_helpdesk_invoice_tickets.xml",

        "sh_helpdesk_timesheet/security/helpdesk_timesheet_security.xml",
        "sh_helpdesk_timesheet/security/ir.model.access.csv",
        "sh_helpdesk_timesheet/views/res_config_setting.xml",
        "sh_helpdesk_timesheet/views/hr_timesheet.xml",
        "sh_helpdesk_timesheet/views/sh_helpdesk_ticket.xml",

        "sh_helpdesk_crm/security/sh_helpdesk_crm_security.xml",
        "sh_helpdesk_crm/views/sh_helpdesk_crm_tickets.xml",

        'sh_helpdesk_task/security/helpdesk_task_security.xml',
        'sh_helpdesk_task/views/sh_helpdesk_ticket.xml',
        'sh_helpdesk_task/views/task.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'sh_all_in_one_helpdesk/static/src/js/time_track.js',
            'sh_all_in_one_helpdesk/static/src/xml/TaskTimeCounter.xml',
            'sh_all_in_one_helpdesk/sh_helpdesk_timesheet/static/src/scss/time_track.scss',
            'sh_all_in_one_helpdesk/static/src/js/helpdesk_ticket_kanban_examples.js',
            'sh_all_in_one_helpdesk/static/src/js/ticket_dashboard.js',
            'sh_all_in_one_helpdesk/static/src/css/ticket_dashboard.css',
            'sh_all_in_one_helpdesk/static/src/xml/**/*',
        ],
        'web.assets_frontend': [
            'sh_all_in_one_helpdesk/static/src/js/portal.js',
            'sh_all_in_one_helpdesk/static/src/css/bootstrap-multiselect.min.css',
            'sh_all_in_one_helpdesk/static/src/js/bootstrap-multiselect.min.js',
            'sh_all_in_one_helpdesk/static/src/css/feedback.scss'
        ],
    },
    "application":
    True,
    "auto_install":
    False,
    "installable":
    True,
    'images': [
        'static/description/background.png',
    ],
    "price":
    100,
    "currency":
    "EUR"
}
