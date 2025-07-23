{
    'name': 'Documentos',
    'summary': 'Módulo de documentos.',
    'description': 'Módulo para la gestión de documentos.',
    'author': 'Contreras Pumamango Gianmarco - gmcontrpuma@gmail.com',
    'website': 'https://github.com/CodigoByte2020',
    'category': 'Tools',
    'version': '16.0.0.0.1',
    'depends': [
        'openeducat_admission',
        'portal',
        'isep_openeducat_custom',
        'isep_sign_sale',
        'isep_website_custom'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/isep_record_request_menus.xml',
        # 'views/record_request_views.xml',
        'views/record_request_list_views.xml',
        'views/portal_templates.xml',
        'views/res_partner_views.xml',
        'views/user_profile_openeducat.xml',
        'wizards/observe_document_views.xml',
        'wizards/observe_partner_document_views.xml'
    ],
    'assets': {
        'web.assets_backend': [
            '/isep_record_request/static/src/xml/ir_attachment_preview.xml',
            '/isep_record_request/static/src/js/ir_attachment_preview.js'
        ]
    },
    'installable': True,
}
