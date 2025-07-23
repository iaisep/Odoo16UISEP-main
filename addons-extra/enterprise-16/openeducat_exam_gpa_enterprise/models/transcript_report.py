# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import models


class TranscriptConfig(models.Model):

    _inherit = 'op.student.progression'

    def print_report(self):
        report = self.env.ref(
            'openeducat_exam_gpa_enterprise.action_report_transcript'
        )
        return report.report_action(self, data=report)
