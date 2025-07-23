# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################
{
    'name': "OpenEduCat Digital Library",
    'summary': """This Module Adds The Feature Of Digital Library To Read Books
    In OpenEduCat. You Can Upload Books & Audiobooks And Publish It.""",
    'author': 'OpenEduCat Inc',
    'sequence': 10,
    'installable': True,
    'website': 'http://www.openeducat.org',
    'auto_install': False,

    'category': 'Education',
    'version': '16.0.1.0',
    'images': [],

    'depends': ['base',
                'website',
                'portal',
                'openeducat_core_enterprise'],

    'data': ['security/ir.model.access.csv',
             'data/digital_library_portal_menu.xml',
             'views/digital_library_read_pdf_website.xml',
             'views/digital_library_website_view.xml',
             'views/material_detail_website.xml',
             'views/op_digital_library_category_view.xml',
             'views/op_digital_library_material_view.xml',
             'views/op_digital_library_enrollment_view.xml',
             'views/menu.xml'],

    'qweb': [],

    'demo': ['demo/author_demo.xml',
             'demo/material_tag_demo.xml',
             'demo/publisher_demo.xml',
             'demo/material_demo.xml',
             'demo/category_demo.xml',
             ],
    'assets': {
        'web.assets_frontend': [
            '/openeducat_digital_library/static/src/css/digital_library.scss',
            '/openeducat_digital_library/static/src/js/script.js',
            '/openeducat_digital_library/static/src/js/my_library.js',
            '/openeducat_digital_library/static/src/js/epub.js',
            '/openeducat_digital_library/static/src/js/jszip.min.js',
            '/openeducat_digital_library/static/src/js/material_detail.js'
        ],
        'web._assets_primary_variables': [
            '/openeducat_digital_library/static/src/css/primary_variables.scss'
        ],
        'web.assets_tests': [
            '/openeducat_digital_library/static/tests/tours/digital_library_test.js',
            '/openeducat_digital_library/static/tests/tours/category_detail_test.js'
        ]
    },
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'Other proprietary',
}
