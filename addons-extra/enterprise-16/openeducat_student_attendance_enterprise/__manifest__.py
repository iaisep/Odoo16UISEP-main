# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

{
    'name': 'OpenEduCat Student Attendance Kiosk',
    'summary': """This module aims to manage student's attendances.
    Keeps account of the attendances of the students
    via kiosk mode and barcode scanner.""",
    'version': '16.0.1.0',
    'category': 'Tools',
    "sequence": 3,
    'complexity': "easy",
    'author': 'OpenEduCat Inc',
    'website': 'http://www.openeducat.org',
    'depends': [
        'openeducat_core',
        'openeducat_attendance_enterprise',
        'barcodes',
        'openeducat_student_progress_enterprise'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/op_student_progression_portal.xml',
        'views/student_attendance_view.xml',
        'views/op_student_view.xml',
        'menus/openeducat_student_attendance_enterprise_menu.xml',
        'reports/report_menu.xml',
        'reports/report_student_attendance_summary.xml',
        'reports/student_badge.xml',
        'reports/attendance_timesheet_progression_report.xml',
    ],
    'qweb': [],
    'images': [
        'static/description/openeducat_student_attendance_kiosk.jpg'
    ],
    'assets': {
        'web.assets_backend': [
            '/openeducat_student_attendance_enterprise/'
            'static/src/scss/student_attendance.scss',
            '/openeducat_student_attendance_enterprise/'
            'static/src/js/student_kanban_view_handler.js',
            '/openeducat_student_attendance_enterprise/'
            'static/src/js/kiosk_confirm.js',
            '/openeducat_student_attendance_enterprise/'
            'static/src/js/kiosk_mode.js',
            '/openeducat_student_attendance_enterprise/'
            'static/src/js/greeting_message.js',
            '/openeducat_student_attendance_enterprise/'
            'static/src/xml/student_attendance.xml',
        ],
        'web.assets_qweb': [
            "/openeducat_student_attendance_enterprise/"
            "static/src/xml/student_attendance.xml",
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'Other proprietary',
    'live_test_url': 'https://www.openeducat.org/plans'
}
