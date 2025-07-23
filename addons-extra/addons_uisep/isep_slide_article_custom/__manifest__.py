{
    'name': 'ISEP - Slide Article Custom',

    'summary': 'Slide Article Custom',
    "description": """
            Slide Article Custom
    """,
    'author': 'Hans Franco Olivos Cerna',
    'category': 'Other Category',
    'license': 'AGPL-3',
    'version': '16.0',
    'depends': [
        'website_slides_survey'
    ],
    'data': [
        'views/slide_slide.xml',
        'views/slide_content_detailed.xml',
        "views/page_24_7.xml",
    ],

    'assets': {
        'web.assets_frontend': [
            'isep_slide_article_custom/static/src/js/slides_course_fullscreen_player.js',
            'isep_slide_article_custom/static/src/xml/custom_html_template.xml',
        ],
    },
    'installable': True,

}
