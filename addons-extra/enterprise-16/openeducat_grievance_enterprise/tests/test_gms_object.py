# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################


import datetime

from .test_gms_common import GMSCommon


class GMSTestObject(GMSCommon):
    def setUp(self):
        super(GMSTestObject, self).setUp()

    def test_gms_grievance_object(self):
        grievance_record = self.env['grievance'].create({
            'grievance_for': 'student',
            'subject': 'Grievance About Grades',
            'student_id': self.env.ref('openeducat_core.op_student_1').id,
            'created_date': datetime.date.today(),
            'description': 'The assignment of a course grade '
                           'to me on some basis other than performance in the course.',
            'grievance_category_id': self.env.ref('openeducat_grievance_enterprise.'
                                                  'grievance_category_object4').id,
            'grievance_team_id': self.env.ref('openeducat_grievance_enterprise.'
                                              'grievance_team_object4').id,
            'course_id': self.env.ref('openeducat_core.op_course_2').id,
            'batch_id': self.env.ref('openeducat_core.op_batch_1').id,
            'academic_year_id': self.env.ref('openeducat_core.academic_year_1').id,
            'academic_term_id': self.env.ref('openeducat_core.academic_term_1').id,
        })
        return grievance_record

    def test_gms_reject_grievance(self):
        grievance_record = self.test_gms_grievance_object()
        for data in grievance_record:
            data.submitted_progressbar()
            data.inreview_progressbar()
            data.reject_progressbar()

    def test_gms_cancel_grievance(self):
        grievance_record = self.test_gms_grievance_object()
        for data in grievance_record:
            data.cancel_progressbar()

    def test_gms_action_grievance(self):
        grievance_record = self.test_gms_grievance_object()
        grievance_action = self.env['wizard.action.taken'].create({
            'action_taken': 'action taken',
            'root_cause_id': self.env.ref(
                'openeducat_grievance_enterprise.grievance_root_cause_object1').id
        })
        for data in grievance_record:
            data.submitted_progressbar()
            data.inreview_progressbar()
            data.send_mail()
            grievance_action.submit_action()
            data.resolve_progressbar()
            data.close_progressbar()
