# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

{
    "name": "Openeducat Attendance Report Xlsx",
    'summary': """This module allows you to manage the student attendance.
    You can print absent report in xlsx format for student.""",
    "author": "OpenEduCat Inc",
    "website": "http://www.openeducat.org",
    "category": "Education",
    "version": "16.0.1.0",
    "license": "Other proprietary",
    "external_dependencies": {"python": ["xlsxwriter", "xlrd"]},
    "depends": ["base", "web"],
    "data": [
        "menu/report.xml"
    ],
    'assets': {
        'web.assets_backend': [
            '/openeducat_attendance_report_xlsx/'
        ]
    },
    "demo": [],
    "installable": True,
}
