{
    'name': 'ISEP - Survey File Question',

    'summary': 'Se añade la opcion de adjuntar archivo en el modulo de encuesta',
    "description": """
            Este particular modulo añade la posibilidad de adjuntar archivos al modulo de encuestas, 
            preparando la funcionalidad para ser usada en el Elearning para la subida de asignaciones, esto mejora el flujo dejando obsoleto el modulo de asignaciones.
            Se deja totalmente independiente.
    """,
    'author': 'Hans Franco Olivos Cerna',
    'category': 'Other Category',
    'license': 'OPL-1',
    'version': '16.0',
    'depends': [
        'survey', 'mail',
    ],
    'assets': {
        'web.assets_backend': [
            'isep_survey_attachment/static/src/css/survey_result.css',
        ],
        'survey.survey_assets': [
            'isep_survey_attachment/static/src/css/survey_front_result.css',
            'isep_survey_attachment/static/src/js/survey_form.js',
        ],
    },
    'data': [
        'views/survey_template_view.xml',
        'views/survey_user_input_line_view.xml',
        'views/survey_view.xml',
    ],
    'installable': True,

}
