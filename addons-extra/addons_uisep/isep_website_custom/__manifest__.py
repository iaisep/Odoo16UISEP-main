# -*- coding: utf-8 -*-
{
    'name': "Isep - Custom website Campus",
    'summary': "Isep - Custom website Campus",
    'description': "Isep - Custom website Campus",
    'author': "Hans Olivos",
    'category': 'website',
    'version': '0.1',
    'depends': ['base','website','website_slides','openeducat_admission','isep_openeducat_custom','openeducat_core_enterprise'],
    'data': [
        'views/user_profile_content.xml',
        'views/user_profile_content_details.xml',
        'views/user_profile_sidebar.xml',
        'views/user_profile.xml',
        'views/user_profile_course.xml',
        'views/website_slides_course_sidebar.xml',
        'views/user_profile_coming_soon.xml',
        'views/portal_dashboard.xml',
        'views/website_menu_campus.xml',
        'views/dashboard_campus.xml',
        'views/user_profile_openeducat.xml',
        'views/user_profile_my_account.xml',

        
        
    ],
    'assets': {
        'web.assets_frontend': [
            '/isep_website_custom/static/src/scss/style.scss',
        ],
    }
}
