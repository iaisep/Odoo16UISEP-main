# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################
import logging

from .test_digital_library_commom import TestDigitalLibraryCommon


class TestDigitalLibraryMaterial(TestDigitalLibraryCommon):

    def setUp(self):
        super(TestDigitalLibraryMaterial, self).setUp()

    def details_of_material(self, case_number, data):
        logging.info('Test Case - %.2f : %s' % (case_number, data.name))
        logging.info('Record Id     : %d' % data.id)
        logging.info('Material Type : %s' % data.material_type)

    def material_a_new_visitor(self):
        data = self.env.ref(
            'openeducat_digital_library.material_a_new_visitor')
        self.details_of_material(1.01, data)
        return data

    def material_a_special_nest(self):
        data = self.env.ref(
            'openeducat_digital_library.material_a_special_nest')
        self.details_of_material(1.02, data)
        return data

    def material_a_very_green_day(self):
        data = self.env.ref(
            'openeducat_digital_library.material_a_very_green_day')
        self.details_of_material(1.03, data)
        return data

    def material_educational_technology(self):
        data = self.env.ref(
            'openeducat_digital_library.material_educational_technology')
        self.details_of_material(1.04, data)
        return data

    def material_java_programming(self):
        data = self.env.ref(
            'openeducat_digital_library.material_java_programming')
        self.details_of_material(1.05, data)
        return data

    def material_python_programming(self):
        data = self.env.ref(
            'openeducat_digital_library.material_python_programming')
        self.details_of_material(1.05, data)
        return data

    def category_material(self):
        material = self.op_digital_library_material.search([])
        material._compute_review_material()
        material._compute_total_reviews_material()
        for data in material:
            material.get_data_of_category(data.id)
            material.get_material_rating_stats_value(data.id)
            material.get_data_of_author_name(data.id)
            material.get_data_of_publisher_name(data.id)


class TestDigitalCategory(TestDigitalLibraryMaterial):

    def setUp(self):
        super(TestDigitalCategory, self).setUp()

    def test_digital_library_category(self):
        category = self.op_digital_library_category.search([])
        category._compute_get_total_material_count()
        category._compute_category_display_name()
