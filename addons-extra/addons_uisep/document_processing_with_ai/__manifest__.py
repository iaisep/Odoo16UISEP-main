{
    'name': "Document Processing with AI",
    'summary': "AI-powered system for analyzing and validating documents in Odoo.",
    'description': """
This module integrates advanced AI functionalities to process, validate, and manage document workflows in Odoo. 
Features include:
- AI-based document classification and analysis.
- Integration with OpenAI GPT for validation and feedback.
- OCR support for extracting text from PDFs and images.
- Flexible configuration of AI parameters for specific document types.
- Automated notifications and comments for document state updates.
    """,
    'author': "",
    'category': 'Tools',
    'version': '1.0',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'isep_record_request',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/custom_ai_parameter_views.xml',
        'data/ir_config_parameter_data.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
