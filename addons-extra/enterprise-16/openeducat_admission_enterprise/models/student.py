# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from datetime import datetime

from odoo import models


class OpStudentFeesDetails(models.Model):
    _inherit = "op.student.fees.details"

    def _cron_create_invoice(self):
        fees_ids = self.env['op.student.fees.details'].search(
            [('date', '<', datetime.today()), ('invoice_id', '=', False)])
        for fees in fees_ids:
            fees.get_invoice()
