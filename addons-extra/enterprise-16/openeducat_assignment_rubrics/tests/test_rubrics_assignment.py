# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from .test_rubrics_assignment_common import RubricsAssignmentCommon


class TestOpRubricTemplate(RubricsAssignmentCommon):

    def setUp(self):
        super(TestOpRubricTemplate, self).setUp()

    def test_case_op_rubric_template(self):
        template = self.env['op.rubric.template'].create({
            'name': 'Percentage Rubric Template',
            'rubrics_type': 'percent',
            'state': 'in_use'
        })
        element1 = self.env['op.rubric.element'].create({
            'name': 'Content',
            'rubrics_type': 'percent',
            'percentage': 20.0,
            'rubrics_template_id': template.id
        })
        element2 = self.env['op.rubric.element'].create({
            'name': 'Figure',
            'rubrics_type': 'percent',
            'percentage': 40.0,
            'rubrics_template_id': template.id
        })
        element3 = self.env['op.rubric.element'].create({
            'name': 'Writting',
            'rubrics_type': 'percent',
            'percentage': 40.0,
            'rubrics_template_id': template.id
        })
        record = self.op_rubric_template.create({
            'name': 'Rubric Test Template',
            'rubrics_type': 'percent',
            'state': 'in_use',
            'rubric_element_line': [element1.id,
                                    element2.id,
                                    element3.id]
        })
        record.act_in_use()
        record.act_cancel()
        record.act_re_open()


class TestOpAssignment(RubricsAssignmentCommon):

    def setUp(self):
        super(TestOpAssignment, self).setUp()

    def test_case_op_assignment(self):
        types = self.op_assignment.search([])
        for record in types:
            if record.rubric_template_id:
                record._check_marks()


class TestOpAssignmentSubLine(RubricsAssignmentCommon):

    def setUp(self):
        super(TestOpAssignmentSubLine, self).setUp()

    def test_case_op_assignment_sub_line(self):
        types = self.op_assignment_sub_line.search([])

        for record in types:
            if record.assignment_id.rubric_template_id:
                record.act_to_assess()
                record.act_accept()


class TestOpAssignmentRubricSubLine(RubricsAssignmentCommon):

    def setUp(self):
        super(TestOpAssignmentRubricSubLine, self).setUp()

    def test_case_op_assignment_rubric_sub_line(self):
        template = self.env['op.rubric.template'].create({
            'name': 'Percentage Rubric Template',
            'rubrics_type': 'percent',
            'state': 'in_use'
        })

        element1 = self.env['op.rubric.element'].create({
            'name': 'Content',
            'rubrics_type': 'percent',
            'percentage': 20.0,
            'rubrics_template_id': template.id
        })
        element2 = self.env['op.rubric.element'].create({
            'name': 'Figure',
            'rubrics_type': 'points',
            'point': 40.0,
            'rubrics_template_id': template.id
        })

        record = self.op_assignment_rubric_sub_line.create({
            'rubric_element_id': element1.id,
            'marks': 50,
            'rubrics_type': 'percent',
            'percentage': 12.0
        })

        record._percentage_error_raise()

        record = self.op_assignment_rubric_sub_line.create({
            'rubric_element_id': element2.id,
            'marks': 40,
            'rubrics_type': 'points',
            'point': 30.0
        })

        record._point_error_raise()
