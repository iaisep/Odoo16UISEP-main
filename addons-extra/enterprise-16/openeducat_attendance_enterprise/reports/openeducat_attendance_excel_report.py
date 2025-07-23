# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import models


class AttendanceXlsx(models.AbstractModel):
    _name = 'report.op.attendance_xlsx'
    _description = 'Openeducat Attendance Report'
    _inherit = 'report.openeducat_attendance_report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
        registers = self.env['op.attendance.register'].search([(
            'id', '=', partners.id)])
        student_row = {}
        row = 1
        col = 4
        r = 3
        col_at = c = 2
        sr_no = 1
        st = []
        total_lectures_taken = []
        pres = {}
        p = 3
        ro = 3
        no_format = workbook.add_format({
            'align': 'center'})
        header_format = workbook.add_format({
            'align': 'center', 'bold': True})
        worksheet = workbook.add_worksheet(registers.name)
        worksheet.write(1, 3, 'Date', header_format)
        worksheet.write(2, 3, 'Lecture', header_format)
        worksheet.set_column('A:A', 10)
        worksheet.set_column('B:B', 22)
        worksheet.set_column('C:C', 22)
        worksheet.set_column('D:D', 12)
        worksheet.set_column('E:BZ', 50)
        worksheet.merge_range(0, 0, 2, 0, 'Serial No.', header_format)
        worksheet.merge_range(0, 1, 2, 1, 'Roll No/Enrollment No', header_format)
        worksheet.merge_range(0, 2, 2, 2, 'Name', header_format)
        worksheet.freeze_panes(0, 3)
        sheets = self.env['op.attendance.sheet'].search([(
            'register_id', '=', registers.id)])
        for sheet in sheets:
            worksheet.write(row, col, str(sheet.attendance_date), header_format)
            if sheet.session_id.id:
                worksheet.write(row + 1, col, sheet.session_id.name, header_format)
            else:
                worksheet.write(row + 1, col, '', header_format)
            total_lectures_taken.append(sheet.session_id.id)
            for student in sheet.attendance_line:
                if student.student_id.id not in st:
                    st.append(student.student_id.id)
                    student_row[student.student_id.id] = r
                    worksheet.write(r, c - 2, sr_no, no_format)
                    worksheet.write(r, c - 1, student.student_id.gr_no, no_format)
                    worksheet.write(r, c, student.student_id.name)
                if student.present:
                    worksheet.write(student_row[student.student_id.id],
                                    col_at + 2, 1, no_format)
                else:
                    worksheet.write(student_row[student.student_id.id],
                                    col_at + 2, 0, no_format)
                r += 1
                sr_no += 1
            col_at += 1
            col += 1
        st.clear()
        for sheet in sheets:
            for student in sheet.attendance_line:
                if student.student_id.id not in st:
                    st.append(student.student_id.id)
                    for i in st:
                        current_sheets = self.env['op.attendance.line'].search(
                            [('attendance_id.register_id', '=', registers.id),
                             ('student_id', '=', i),
                             ('present', '=', True)])
                        cur_student = self.env['op.student'].search([('id', '=', i)])
                        pres.update({
                            cur_student.id: len(current_sheets)
                        })
                        worksheet.write(ro, col + 1, pres[cur_student.id], no_format)
                    ro += 1
                worksheet.write(student_row[student.student_id.id], col + 2,
                                len(total_lectures_taken), no_format)
        worksheet.merge_range(0, col, 2, col, 'Attendance in Percentage(%)',
                              header_format)
        worksheet.merge_range(0, col + 1, 2, col + 1, 'Total Lectures Attended',
                              header_format)
        worksheet.merge_range(0, col + 2, 2, col + 2, 'Total Lectures Taken',
                              header_format)
        for i in st:
            cur_student = self.env['op.student'].search([('id', '=', i)])
            percentage = (pres[cur_student.id] / len(total_lectures_taken)) * 100
            worksheet.write(p, col, format(percentage, ".2f"), no_format)
            p += 1
        workbook.close()
