from odoo.tests import common


class AssignmentGradingCommon(common.TransactionCase):
    def setUp(self):
        super(AssignmentGradingCommon, self).setUp()
        self.op_assignment_subline = self.env["op.assignmnet.sub.line"]
