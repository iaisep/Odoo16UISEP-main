from .test_assignment_gradding_common import AssignmentGradingCommon


class TestAssignmnetGrading(AssignmentGradingCommon):
    def setUp(self):
        super(TestAssignmnetGrading, self).setUp()

    def test_case_op_assignmnet_sub_line(self):
        types = self.op_assignment_subline.search([])

        for record in types:
            record.hide_grade()
