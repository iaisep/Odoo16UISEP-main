# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################
import logging

from .test_material import TestDigitalLibraryMaterial


class TestCourse(TestDigitalLibraryMaterial):

    def setUp(self):
        super(TestCourse, self).setUp()
        logging.info('Test cases for Course Material ::')
        self.material_a_new_visitor()
        self.material_a_special_nest()
        self.material_a_very_green_day()
        self.material_educational_technology()
        self.material_java_programming()
        self.category_material()
        self.material_python_programming()

    def details_of_category(self, case_number, data):
        logging.info('Test Case - %d : %s' % (case_number, data.name))
        if data.material_ids:
            logging.info('Information of Material ::')
            for material in data.material_ids:
                logging.info('  Material        : %s' % material.name)

    def demo_material_1(self):
        data = self.env.ref(
            'openeducat_digital_library.category_library_kids')
        if not data:
            raise AssertionError(
                'Error in data, please check for '
                'demo data : openeducat_digital_library.category_library_kids')
        self.details_of_category(1, data)
        return data

    def demo_material_2(self):
        data = self.env.ref(
            'openeducat_digital_library.category_library_technology')
        if not data:
            raise AssertionError(
                'Error in data, please check for '
                'demo data : openeducat_digital_library.category_library_technology')
        self.details_of_category(2, data)
        return data

    def demo_material_3(self):
        data = self.env.ref(
            'openeducat_digital_library.category_library_programming')
        if not data:
            raise AssertionError(
                'Error in data, please check for '
                'demo data : openeducat_digital_library.category_library_programming')
        self.details_of_category(3, data)
        return data

    def test_cases(self):
        logging.info('Test Cases For Material ::')
        self.demo_material_1()
        self.demo_material_2()
        self.demo_material_3()
