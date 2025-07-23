{
    'name': 'OpenEduCat Live',
    'summary': """OpenEduCat Live is very important part of
    any educational institute. OpenEduCat Live module from OpenEduCat helps you managing
    all type of the Meeting.""",
    'version': '16.0.1.0',
    'category': 'Productivity/Discuss',
    'sequence': 145,
    'author': 'OpenEduCat Inc',
    'company': 'OpenEduCat Inc.',
    'depends': ['base', 'mail', 'openeducat_core_enterprise',
                'openeducat_meeting_enterprise',
                'openeducat_online_tools_enterprise'],
    'website': 'http://www.openeducat.org',
    'data': [
        'security/ir.model.access.csv',
        'security/openeducat_live_security.xml',
        'views/calendar_event.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'assets': {
        'web.assets_qweb': [
        ],
        'mail.assets_messaging': [
            'openeducat_live/static/src/js/*.js',
            # 'openeducat_live/static/src/widgets/*.js',
            'openeducat_live/static/src/css/*.css',
            'openeducat_live/static/src/scss/*.scss',
            'openeducat_live/static/src/create_meet_calendar/create_meet_calendar.js',
            'openeducat_live/static/src/xml/*.xml',
        ],
        'mail.assets_core_messaging': [
            'openeducat_live/static/src/js/discuss.js',
        ],
        'web.assets_backend': [
            'openeducat_live/static/src/xml/channel_invitation_form.xml',
            'openeducat_live/static/src/xml/call_action_list.xml',
        ],
        'mail.assets_discuss_public': [
            'openeducat_live/static/src/js/*.js',
            'openeducat_live/static/src/xml/*.xml',
            'openeducat_live/static/src/css/*.css',
            'openeducat_live/static/src/scss/*.scss',
        ],
    },
    'license': 'Other proprietary',
}
