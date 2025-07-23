# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################
from odoo import fields, http
from odoo.http import request

from odoo.addons.portal.controllers.portal import CustomerPortal

PPG = 10
PPR = 4


class OpDigitalLibraryController(CustomerPortal):

    @http.route(['/digital-library',
                 '/digital-library/page/<int:page>',
                 '/digital-library/category/<model'
                 '("op.digital.library.category"):category>',
                 ], type="http", auth="public", sitemap=False,
                website=True)
    def digital_library(self, search='', page=0, filter_name='',
                        category=False, ppg=False, **post):
        material_domain = []
        total_material = 0
        category_ref = request.env['op.digital.library.category'].sudo()
        if ppg:
            try:
                ppg = int(ppg)
            except ValueError:
                ppg = PPG
            post["ppg"] = ppg
        else:
            ppg = PPG
        if search:
            post["search"] = search
            for term in search.split(" "):
                if filter_name == 'name' or filter_name == '':
                    material_domain += [('name', 'ilike', term)]
                if filter_name == 'author':
                    material_domain += [('author_ids', 'ilike', term)]
                if filter_name == 'publisher':
                    material_domain += [('publisher_ids', 'ilike', term)]
                if filter_name == 'tag':
                    material_domain += [('material_tags', 'ilike', term)]
        if category:
            domain = [('id', '=', category.id)]
            materials = category_ref.sudo().search(domain).material_ids
        else:
            all_categories = category_ref.search([])
            all_material_ids = [cat.id for cat in all_categories]
            materials = category_ref.search(
                [('id', 'in', all_material_ids)]).material_ids
        url = "/digital-library"
        total_count = len(materials)
        pager = request.website.pager(
            url=url, total=total_count, page=page, step=ppg, scope=7,
            url_args=post)
        if request.env.user == request.website.user_id:
            public_user = True
        else:
            public_user = False
        if category:
            categories = category_ref.sudo().search(
                [('parent_id', '=', category.id)])
        else:
            categories = category_ref.sudo().search([('parent_id', '=', False)])
            temp_material_ids = [mat.id for mat in materials]
            material_domain += [('id', 'in', temp_material_ids)]
            materials = materials.sudo().search(material_domain,
                                                limit=ppg, offset=pager['offset'])
        return request.render('openeducat_digital_library.'
                              'op_digital_library_category_web_template', {
                                  'category_ids': categories,
                                  'category': category,
                                  'total_material': total_material,
                                  'materials': materials,
                                  'public_user': public_user,
                                  'pager': pager,
                                  'search': search,
                                  'rows': 3,
                              })

    @http.route(['/digital-library/add-to-list/<material_id>'],
                type='http', auth='user', website=True)
    def add_to_reading_list(self, material_id):
        material_model = request.env['op.digital.library.material'].sudo(). \
            search([('id', '=', material_id)])
        enrollment_model = request.env['op.digital.library.enrollment'].sudo()
        enrolled = enrollment_model.search(
            [('user_id', '=', request.env.user.id),
             ('material_id', '=', material_model.id)])
        if enrolled:
            return request.redirect('/my-library')
        else:
            enrollment_model.create({
                'user_id': request.env.user.id,
                'material_id': material_id,
                'enrollment_date': fields.Datetime.now(),
                'state': 'reading_list'
            })
            return request.redirect('/my-library')

    @http.route(['/digital-library/add-review'],
                type='json', auth='public', website=True)
    def add_review_material_list(self, **post):
        review_model = request.env['op.digital.library.material.review']
        if post:
            post.update({
                'user_id': int(post.get('user_id')) or False
            })
        create_review = review_model.sudo().create(post)
        if create_review.id:
            code = 'success'
        else:
            code = 'error'

        return code

    @http.route(['''/digital-library/material/<material_id>'''],
                type="http", auth="public", sitemap=False, website=True)
    def digital_library_category_detail(self, material_id=0):
        material = request.env['op.digital.library.material'].sudo() \
            .search([('id', '=', material_id)])

        return request.render('openeducat_digital_library.'
                              'op_digital_library_material_web_template', {
                                  'material': material,
                              })

    @http.route(['/library/enroll/<int:material_id>'],
                type='http', auth="user", website=True)
    def enroll_course(self, material_id=0):
        library_model = request.env['op.digital.library.enrollment']
        enrollment = library_model.sudo().search(
            [('user_id', '=', request.env.user.id),
             ('material_id', '=', material_id)])
        if not enrollment:
            library_model.sudo().create({
                'user_id': request.env.user.id,
                'material_id': material_id,
                'enrollment_date': fields.Datetime.now(),
            })
        return request.redirect('/my-library')

    @http.route(['/my-library', '/my-library/<int:student_id>'],
                type='http', auth="user", website=True)
    def op_digital_my_library(self, student_id=None):
        if student_id:
            student = request.env['op.student'].sudo().search([('id', '=', student_id)])
            enrollments = request.env['op.digital.library.enrollment']. \
                sudo().search([('user_id', '=', student.user_id.id)])
        else:
            enrollments = request.env['op.digital.library.enrollment']. \
                sudo().search([('user_id', '=', request.env.uid)])

        if not enrollments:
            return request.redirect('/digital-library')

        return request.render('openeducat_digital_library.'
                              'op_digital_my_library_web_template', {
                                  'enrollments': enrollments
                              })

    @http.route(['/digital-library/read/<material_id>'],
                type='http', auth="user", website=True)
    def op_digital_read_mode_library(self, material_id=0):
        enrollments = request.env['op.digital.library.material'].sudo().search(
            [('id', '=', int(material_id))])
        access_model = request.env['op.digital.library.enrollment'].sudo().search(
            [('material_id', '=', int(material_id)),
             ('user_id', '=', request.env.uid)]
        )
        if access_model:
            access_model.update({
                'last_access': fields.Datetime.now()
            })
        else:
            enrollment_model = request.env['op.digital.library.enrollment'].sudo()
            enrollment_model.create({
                'user_id': request.env.user.id,
                'material_id': material_id,
                'enrollment_date': fields.Datetime.now(),
                'last_access': fields.Datetime.now(),
                'state': 'in_progress',
            })
        pdf = enrollments.material_data
        if enrollments.material_type == 'audiobook':
            audio = "data:audio/mp3;base64," + enrollments. \
                material_data.decode("utf-8")
        else:
            audio = False

        return request.render('openeducat_digital_library.'
                              'op_digital_library_read_mode_web_template', {
                                  'enrollments': enrollments,
                                  'pdf': pdf,
                                  'audio': audio
                              })

    @http.route('/library/audiobook/<int:material_id>')
    def get_last_read_page_number(self, material_id):
        material = request.env['op.digital.library.material'].sudo(). \
            browse(material_id)
        access_model = request.env['op.digital.library.enrollment'].sudo().search(
            [('material_id', '=', int(material_id)), ('user_id', '=', request.env.uid)]
        )
        access_model.update({
            'last_access': fields.Datetime.now()
        })
        data = "data:audio/mp3;base64," + material.material_data.decode("utf-8")
        return {
            'data': data
        }

    @http.route('/digital-library/embed/<int:material_id>', type='http',
                auth='public', website=True)
    def digital_library_materials_embed(self, material_id, **kw):
        template = 'openeducat_digital_library.iframe_html_div'
        material = request.env['op.digital.library.material'].sudo(). \
            browse(material_id)
        return request.render(template, {'enrollments': material})


class CustomerPortal(CustomerPortal):

    @http.route()
    def home(self, **kw):
        response = super(CustomerPortal, self).home(**kw)
        count = request.env['op.digital.library.enrollment'].sudo() \
            .search_count([('user_id', '=', request.env.uid)])
        response.qcontext.update({
            'my_library_count': count
        })
        return response
