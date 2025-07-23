# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################
import math

from odoo import api, fields, models


class OpDigitalLibraryMaterial(models.Model):
    _name = 'op.digital.library.material'
    _description = 'Material For Digital Library'

    def _default_language(self):
        lang_code = self.env['ir.default'].get('res.partner', 'lang')
        def_lang_id = self.env['res.lang']._lang_get_id(lang_code)
        return def_lang_id or self._active_languages()[0]

    name = fields.Char(string="Name", required=True)
    material_cover = fields.Image(string="Cover Image")
    material_description = fields.Html(string="Description")
    author_ids = fields.Many2many('op.digital.library.author',
                                  string="Author(s)", required=True)
    publisher_ids = fields.Many2many('op.digital.library.publisher',
                                     string="Publisher(s)", required=True)
    material_edition = fields.Char(string="Edition", required=True)
    isbn_code = fields.Char(string="ISBN Code")
    material_source = fields.Char(string="Source", required=True)
    publish_online = fields.Boolean(string="Publish Online", default=True)
    material_tags = fields.Many2many('op.digital.library.material.tag',
                                     string="Tag(s)")
    material_type = fields.Selection([('pdf', 'PDF'),
                                      ('epub', 'ePub'),
                                      ('audiobook', 'AudioBook')],
                                     required=True, string="Material Type")
    material_data = fields.Binary(string="Upload Here",
                                  attachment=True, required=True)
    material_review_line = fields.One2many('op.digital.library.material.review',
                                           'material_id', string="Reviews")
    material_enrollment_line = fields.One2many('op.digital.library.enrollment',
                                               'material_id',
                                               string="Enrollments")
    rating = fields.Float(string="Rating", compute="_compute_review_material")
    language_id = fields.Many2one('res.lang', string='Language',
                                  default=_default_language)
    total_reviews = fields.Integer(string="Total Review",
                                   compute="_compute_total_reviews_material")

    @api.depends('material_review_line')
    def _compute_review_material(self):
        if self.material_review_line:
            total_review = len(self.material_review_line)
            total_rating = 0
            for review in self.material_review_line:
                total_rating = total_rating + review.rating
            final_rating = total_rating / total_review
            self.rating = "{:.2f}".format(round(final_rating, 2))
        else:
            self.rating = 0

    @api.depends('material_review_line')
    def _compute_total_reviews_material(self):
        if self.material_review_line:
            self.total_reviews = len(self.material_review_line)
        else:
            self.total_reviews = 0

    def get_data_of_category(self, material_id):
        category_value = ''
        material = self.env['op.digital.library.material'].sudo() \
            .search([('id', '=', material_id)])
        categories = self.env['op.digital.library.category'].sudo().search([])
        for category in categories:
            if material in category.sudo().material_ids:
                category_value = category_value + ', ' + category.name

        return category_value[2:]

    def get_material_rating_stats_value(self, material_id):
        material = self.env['op.digital.library.material'].sudo() \
            .search([('id', '=', material_id)])
        rate_floor = math.floor(material.rating)
        rate_decimal = material.rating - rate_floor
        rate_empty = 5 - (rate_floor + math.ceil(rate_decimal))

        return {
            'rate_floor': rate_floor,
            'rate_decimal': rate_decimal,
            'rate_empty': rate_empty,
        }

    def get_data_of_author_name(self, material_id):
        author_value = ''
        authors = self.env['op.digital.library.material'].sudo() \
            .search([('id', '=', material_id)]).author_ids
        for author in authors:
            author_value = author_value + ', ' + author.name

        return author_value[2:]

    def get_data_of_publisher_name(self, material_id):
        publisher_value = ''
        publishers = self.env['op.digital.library.material'].sudo() \
            .search([('id', '=', material_id)]).publisher_ids
        for publisher in publishers:
            publisher_value = publisher_value + ', ' + publisher.name

        return publisher_value[2:]
