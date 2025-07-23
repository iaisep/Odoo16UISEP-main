{
    'name': 'ISEP - Survey',

    'summary': 'Alguna adaptaciones para la integracion academica',
    "description": """
            Alguna adaptaciones para la integracion academica
    """,
    'author': 'Hans Franco Olivos Cerna',
    'category': 'Other Category',
    'license': 'OPL-1',
    'version': '16.0',
    'depends': [
        'survey', 'mail', 'isep_survey_attachment','website_slides_survey','openeducat_admission'
    ],
    'data': [
        'views/survey_view.xml',
        'views/survey_xpath.xml',
        'views/survey_fill_form_done_template.xml',  
    ],

    'assets': {
        'web.assets_frontend': [
            'isep_survey/static/src/js/slides_course_fullscreen_player.js',
            'isep_survey/static/src/xml/website_slides_fullscreen.xml',
        ],
    },
    'installable': True,

}
