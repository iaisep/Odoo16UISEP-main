# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################
import logging

from .test_course_material import TestCourseMaterial


class TestCourse(TestCourseMaterial):

    def setUp(self):
        super(TestCourse, self).setUp()
        logging.info('Test cases for Course Material ::')
        self.material_python_intro_course()
        self.material_python_words()
        self.material_python_anaconda_bundle()
        self.material_python_install()
        self.material_python_syntax_pdf()
        self.material_python_variable()
        self.material_python_string_number()
        self.material_python_functions()
        self.material_python_cnd_image()
        self.material_python_sequence_list()
        self.material_python_iteration()
        self.material_python_files()
        self.material_python_files_rw()
        self.material_french_video()
        self.material_french_pdf()
        self.material_french_image()
        self.material_sell_video()
        self.material_sell_pdf()
        self.material_sell_image()
        self.message_log = self.env['mail.message']
        self.rating = self.env['rating.rating']

    def details_of_course(self, case_number, data):
        logging.info('Test Case - %d : %s' % (case_number, data.name))
        logging.info('Code          : %s' % data.code)
        if data.faculty_ids:
            logging.info('Information of Faculty ::')
            for faculty in data.faculty_ids:
                logging.info('  Faculty        : %s' % faculty.name)
        if data.category_ids:
            logging.info('Information of Categories ::')
            for category in data.category_ids:
                logging.info('  Category       : %s' % category.name)
        if data.suggested_course_ids:
            logging.info('Information of Suggested Course ::')
            for suggested in data.suggested_course_ids:
                logging.info('  Course         : %s' % suggested.name)
        logging.info('State         : %s' % data.state)
        logging.info('Visibility    : %s' % data.visibility)
        if data.visibility == 'invited_user':
            logging.info('Invited Users Detail.....')
            for user in data.invited_users_ids:
                logging.info('  %s ', user.name)
        logging.info('Navigation Policy : %s' % data.navigation_policy)
        logging.info('Course Section: ')
        for section in data.course_section_ids:
            logging.info('  Sequence      : %d' % section.sequence)
            logging.info('  Section       : %s' % data.name)
            logging.info('  Material      : ')
            for material in section.section_material_ids:
                logging.info('       %d : %s' % (material.sequence,
                                                 material.material_id.name))

        messages = self.message_log.search(
            [('res_id', '=', data.id), ('model', '=', 'op.course')])
        if messages:
            logging.info('Comment details ::')
            for message in messages:
                rate = self.rating.search([('message_id', '=', message.id)])
                format_str = '%s'
                format_var = (message.body)
                if rate:
                    format_str = '  %s : %.2f'
                    format_var = (message.body, rate.rating)
                logging.info(format_str % format_var)

    def demo_course_1(self):
        data = self.env.ref(
            'openeducat_lms.demo_course_1')
        if not data:
            raise AssertionError(
                'Error in data, please check for '
                'demo data : openeducat_lms.demo_course_1')
        self.details_of_course(1, data)
        return data

    def demo_course_2(self):
        data = self.env.ref(
            'openeducat_lms.demo_course_2')
        if not data:
            raise AssertionError(
                'Error in data, please check for '
                'demo data : openeducat_lms.demo_course_2')
        self.details_of_course(2, data)
        return data

    def demo_course_3(self):
        data = self.env.ref(
            'openeducat_lms.demo_course_3')
        if not data:
            raise AssertionError(
                'Error in data, please check for '
                'demo data : openeducat_lms.demo_course_3')
        self.details_of_course(3, data)
        return data

    def test_cases(self):
        logging.info('Test Cases For Course ::')
        self.demo_course_1()
        self.demo_course_2()
        self.demo_course_3()
