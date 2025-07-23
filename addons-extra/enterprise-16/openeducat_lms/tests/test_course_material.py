# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################
import logging

from .test_lms_common import TestLmsCommon


class TestCourseMaterial(TestLmsCommon):

    def setUp(self):
        super(TestCourseMaterial, self).setUp()

    def details_of_material(self, case_number, data, video=False):
        logging.info('Test Case - %.2f : %s' % (case_number, data.name))
        logging.info('Record Id     : %d' % data.id)
        logging.info('Material Type : %s' % data.material_type)
        if video:
            logging.info('Document Url  : %s' % data.url)
            logging.info('Document Id   : %s' % data.document_id)

    def material_python_intro_course(self):
        data = self.env.ref(
            'openeducat_lms.material_python_intro_course')
        data.on_change_url()
        self.details_of_material(1.01, data, True)
        return data

    def material_python_words(self):
        data = self.env.ref(
            'openeducat_lms.material_python_words')
        data.on_change_url()
        self.details_of_material(1.02, data, True)
        return data

    def material_python_anaconda_bundle(self):
        data = self.env.ref(
            'openeducat_lms.material_python_anaconda_bundle')
        data.on_change_url()
        self.details_of_material(1.03, data, True)
        return data

    def material_python_install(self):
        data = self.env.ref(
            'openeducat_lms.material_python_install')
        data.on_change_url()
        self.details_of_material(1.04, data, True)
        return data

    def material_python_syntax_pdf(self):
        data = self.env.ref(
            'openeducat_lms.material_python_syntax_pdf')
        data.on_change_url()
        self.details_of_material(1.05, data, True)
        return data

    def material_python_variable(self):
        data = self.env.ref(
            'openeducat_lms.material_python_variable')
        data.on_change_url()
        self.details_of_material(1.06, data, True)
        return data

    def material_python_string_number(self):
        data = self.env.ref(
            'openeducat_lms.material_python_string_number')
        data.on_change_url()
        self.details_of_material(1.07, data, True)
        return data

    def material_python_functions(self):
        data = self.env.ref(
            'openeducat_lms.material_python_functions')
        data.on_change_url()
        self.details_of_material(1.08, data, True)
        return data

    def material_python_cnd_image(self):
        data = self.env.ref(
            'openeducat_lms.material_python_cnd_image')
        data.on_change_url()
        self.details_of_material(1.09, data, True)
        return data

    def material_python_sequence_list(self):
        data = self.env.ref(
            'openeducat_lms.material_python_sequence_list')
        data.on_change_url()
        self.details_of_material(1.10, data, True)
        return data

    def material_python_iteration(self):
        data = self.env.ref(
            'openeducat_lms.material_python_iteration')
        data.on_change_url()
        self.details_of_material(1.11, data, True)
        return data

    def material_python_files(self):
        data = self.env.ref(
            'openeducat_lms.material_python_files')
        data.on_change_url()
        self.details_of_material(1.12, data, True)
        return data

    def material_python_files_rw(self):
        data = self.env.ref(
            'openeducat_lms.material_python_files_rw')
        data.on_change_url()
        self.details_of_material(1.13, data, True)
        return data

    def material_french_video(self):
        data = self.env.ref(
            'openeducat_lms.material_french_video')
        if not data:
            raise AssertionError(
                'Error in data, please check for '
                'demo data : openeducat_lms.material_french_video')
        data.on_change_url()
        self.details_of_material(2.1, data, True)
        return data

    def material_french_pdf(self):
        data = self.env.ref('openeducat_lms.material_french_pdf')
        if not data:
            raise AssertionError(
                'Error in data, please check for '
                'demo data : openeducat_lms.material_french_pdf')
        self.details_of_material(2.2, data)
        return data

    def material_french_image(self):
        data = self.env.ref('openeducat_lms.material_french_image')
        if not data:
            raise AssertionError(
                'Error in data, please check for '
                'demo data : openeducat_lms.material_french_image')
        self.details_of_material(2.3, data)
        return data

    def material_sell_video(self):
        data = self.env.ref(
            'openeducat_lms.material_sell_video')
        if not data:
            raise AssertionError(
                'Error in data, please check for '
                'demo data : openeducat_lms.material_sell_video')
        data.on_change_url()
        self.details_of_material(3.1, data, True)
        return data

    def material_sell_pdf(self):
        data = self.env.ref('openeducat_lms.material_sell_pdf')
        if not data:
            raise AssertionError(
                'Error in data, please check for '
                'demo data : openeducat_lms.material_sell_pdf')
        self.details_of_material(3.2, data)
        return data

    def material_sell_image(self):
        data = self.env.ref('openeducat_lms.material_sell_image')
        if not data:
            raise AssertionError(
                'Error in data, please check for '
                'demo data : openeducat_lms.material_sell_image')
        self.details_of_material(3.3, data)
        return data

    def course_material(self):

        material = self.op_material.search([])
        material._compute_total()
        material.website_lms_publish_button()
        material._compute_get_embed_code()
        material.action_onboarding_material_layout()


class TestLmsOnboard(TestLmsCommon):

    def setUp(self):
        super(TestLmsOnboard, self).setUp()

    def test_lms_onboard(self):
        onboard = self.lms_onboard.search([])
        onboard.action_close_lms_onboarding()
        onboard.action_lms_onboarding_course_layout()
        onboard.action_onboarding_material_layout()
        onboard.action_onboarding_enrollment_layout()
        onboard.action_onboarding_course_category_layout()
        onboard.update_lms_onboarding_state()


class TestLmsCourse(TestLmsCommon):

    def setUp(self):
        super(TestLmsCourse, self).setUp()

    def test_lms_course(self):
        lms_course = self.lms_op_course.search([])
        lms_course._compute_get_image()
        lms_course._compute_enrolled_users()
        lms_course._compute_kanban_dashboard_graph()
        lms_course._compute_graph_data()
        lms_course.get_lms_bar_graph_datas()
        lms_course.action_lms_onboarding_course_layout()
        lms_course.action_view_material()
        lms_course.action_view_users()
        lms_course.action_course_completed()


class TestOpCourseSection(TestLmsCommon):

    def setUp(self):
        super(TestOpCourseSection, self).setUp()

    def test_course_section(self):
        section = self.op_course_section.search([])
        section._compute_total_time()


class TestOpCourseMaterial(TestLmsCommon):

    def setUp(self):
        super(TestOpCourseMaterial, self).setUp()

    def test_course_material(self):
        section = self.op_course_material.search([])
        len(section)


class TestMaterialReminder(TestLmsCommon):

    def setUp(self):
        super(TestMaterialReminder, self).setUp()

    def test_material_reminder(self):
        reminder = self.material_reminder.search([])
        reminder.get_base_domain()
        reminder.send_reminder()
        data = self.env['op.material'].create({
            'name': 'Learn to Speak',
            'auto_publish': True,
            'auto_publish_type': 'wait_until',
            'wait_until_date': '2019-03-18',
            'total_time': '0000'
        })
        ds = self.material_reminder.create({
            'material_id': data.id
        })
        ds.send_reminder()

        res = self.env['op.material'].create({
            'name': 'Python elearning',
            'auto_publish': True,
            'auto_publish_type': 'wait_until_duration',
            'wait_until_duration': '5',
            'wait_until_duration_period': 'minutes',
            'total_time': '00'
        })
        data = self.material_reminder.create({
            'material_id': res.id
        })
        data.send_reminder()


class TestOpQuizResult(TestLmsCommon):

    def setUp(self):
        super(TestOpQuizResult, self).setUp()

    def test_quiz_result(self):
        result = self.op_quiz_result.search([])
        for data in result:
            data.get_answer_data()


class TestCourseInvitation(TestLmsCommon):

    def setUp(self):
        super(TestCourseInvitation, self).setUp()

    def test_course_invitation(self):
        result = self.course_invitation.search([])
        result.send_invitation()
