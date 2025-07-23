{
    'name': 'OpenEduCat Quiz Anti Cheating Management',
    'summary': """Faculty can configure Face Tracking with warning limit and
    warning state like In Progress After warning, Permission from admin and Submit.""",
    'version': '16.0.1.0',
    'category': 'Education',
    'website': 'http://www.openeducat.org',
    'author': "OpenEduCat Inc",
    'depends': ['openeducat_quiz'],
    'data': [
        'security/ir.model.access.csv',
        'views/quiz_view.xml',
        'views/start_page.xml',
        'views/result_view.xml',
        'menus/op_menu.xml',
    ],
    'demo': [],
    'assets': {
        'web.assets_frontend': [
            "https://cdn.jsdelivr.net/npm/"
            "html2canvas@1.0.0-rc.7/dist/html2canvas.min.js",
            "/openeducat_quiz_anti_cheating/static/src/js/base64js.min.js",
            "/openeducat_quiz_anti_cheating/static/src/js/face-api.js",
            "/openeducat_quiz_anti_cheating/static/src/js/faceDetectionControls.js",
            # "/openeducat_quiz_anti_cheating/static/src/js/materialize.min.js",
            "/openeducat_quiz_anti_cheating/static/src/css/facestyles.css",
            "/openeducat_quiz_anti_cheating/static/src/css/warningbar.css",
            "/openeducat_quiz_anti_cheating/"
            "static/src/js/website_anti_cheating_quiz.js",
            "https://d3js.org/d3.v4.min.js"
        ], },
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'Other proprietary',
    'live_test_url': 'https://www.openeducat.org/plans'
}
