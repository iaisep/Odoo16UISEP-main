# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import models


class PartnerXlsx(models.AbstractModel):
    _name = "report.openeducat_attendance_report_xlsx.partner_xlsx"
    _inherit = "report.openeducat_attendance_report_xlsx.abstract"
    _description = "Partner XLSX Report"

    def generate_xlsx_report(self, workbook, data, partners):
        sheet = workbook.add_worksheet("Report")
        i = 0
        for obj in partners:
            bold = workbook.add_format({"bold": True})
            sheet.write(i, 0, obj.name, bold)
            i += 1
