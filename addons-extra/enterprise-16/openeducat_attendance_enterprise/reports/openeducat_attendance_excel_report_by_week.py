# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import models


class AttendanceXlsxByWeek(models.AbstractModel):
    _name = 'report.op.attendance_xlsx_by_week'
    _description = 'Openeducat Attendance Report By Week'
    _inherit = 'report.openeducat_attendance_report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
        student_row = {}
        col = {}
        data = {}
        count_heading = 0
        count = 0
        r = 3
        col_at = c = 2
        sr_no = 1
        st = []
        row = 1
        b = 4
        col_week = 5
        pres = {}
        ro = 3
        total_lectures_taken = []
        registers = self.env['op.attendance.register'].search([(
            'id', '=', partners.id)])
        no_format = workbook.add_format({
            'align': 'center'})
        header_format = workbook.add_format({
            'align': 'center', 'bold': True})
        reg_name = registers.name + " Weekly Attendance"
        weekly_worksheet = workbook.add_worksheet(reg_name)
        weekly_worksheet.write(1, 3, 'Date', header_format)
        weekly_worksheet.write(2, 3, 'Lecture', header_format)
        weekly_worksheet.set_column('A:A', 10)
        weekly_worksheet.set_column('B:B', 22)
        weekly_worksheet.set_column('C:C', 22)
        weekly_worksheet.set_column('D:D', 12)
        weekly_worksheet.set_column('E:BZ', 50)
        weekly_worksheet.merge_range(0, 0, 2, 0, 'Serial No.', header_format)
        weekly_worksheet.merge_range(0, 1, 2, 1, 'Roll No/Enrollment No',
                                     header_format)
        weekly_worksheet.merge_range(0, 2, 2, 2, 'Name', header_format)
        weekly_worksheet.freeze_panes(0, 3)

        sheets = self.env['op.attendance.sheet'].search([(
            'register_id', '=', registers.id)])
        week_dates = {}
        for sheet in sheets:
            year, week_num, day_of_week = sheet.attendance_date.isocalendar()
            if week_dates.get(week_num):
                week_dates[week_num].append({
                    'date': sheet.attendance_date,
                    'sheet_id': sheet.id,
                })
            else:
                week_dates[week_num] = [{
                    'date': sheet.attendance_date,
                    'sheet_id': sheet.id
                }]
            for line in sheet.attendance_line:
                if data.get(week_num):
                    if data[week_num].get(line.student_id.id):
                        att = 1 if line.present else 0
                        data[week_num][line.student_id.id] = \
                            data[week_num][line.student_id.id] + att
                    else:
                        data[week_num].update({
                            line.student_id.id: 1 if line.present else 0
                        })
                else:
                    data[week_num] = {
                        line.student_id.id: 1 if line.present else 0
                    }
        col_w = col_week
        x = 0
        for key, values in sorted(week_dates.items()):
            y = a = len(values)
            if x > 0:
                y += 1
                weekly_worksheet.merge_range(0, col_w - 1, 0, col_w + y - 1,
                                             "Week - " + str(key), header_format)
            else:
                weekly_worksheet.merge_range(0, col_w - 1, 0, col_w + y - 1,
                                             "Week - " + str(key), header_format)
                x += 1
            col_w += y + 1

            for elements in values:
                weekly_worksheet.write(row, b, str(elements['date']), header_format)
                sheets = self.env['op.attendance.sheet'].search([(
                    'id', '=', elements['sheet_id'])])
                for sheet in sheets:
                    if sheet.session_id.id:
                        weekly_worksheet.write(row + 1, b, sheet.session_id.name,
                                               header_format)
                    else:
                        weekly_worksheet.write(row + 1, b, '', header_format)
                    total_lectures_taken.append(sheet.id)
                    for student in sheet.attendance_line:
                        if student.student_id.id not in st:
                            st.append(student.student_id.id)
                            student_row[student.student_id.id] = r
                            weekly_worksheet.write(r, c - 2, sr_no, no_format)
                            weekly_worksheet.write(r, c - 1, student.student_id.gr_no,
                                                   no_format)
                            weekly_worksheet.write(r, c, student.student_id.name)
                            for i in st:
                                current_sheets = self.env['op.attendance.line'].search(
                                    [('attendance_id', '=', sheet.id),
                                     ('student_id', '=', i),
                                     ('present', '=', True)])
                                cur_student = self.env['op.student'].search([(
                                    'id', '=', i)])
                                pres.update({
                                    cur_student.id: len(current_sheets)
                                })
                        if student.present:
                            weekly_worksheet.write(student_row[student.student_id.id],
                                                   col_at + 2, 1, no_format)
                        else:
                            weekly_worksheet.write(student_row[student.student_id.id],
                                                   col_at + 2, 0, no_format)
                        r += 1
                        sr_no += 1
                    col_at += 1
                b += 1
            col[key] = {
                'col': b,
                'total': a,
            }
            weekly_worksheet.write(row, b, 'Percentage', header_format)
            b += 1
            col_at += 1
            if count_heading >= 1:
                weekly_worksheet.write(row, b, 'Total Percentage of Weeks Till Now',
                                       header_format)
                b += 1
                col_at += 1
            count_heading += 1
        for key, value in data.items():
            for k, v in value.items():
                percentage = (v / col[key]['total']) * 100
                weekly_worksheet.write(student_row[k], col[key]['col'],
                                       format(percentage, ".2f"), no_format)
        week = {}
        key_len = 1
        prev_k = False
        for key, value in sorted(data.items()):
            week[key] = {}
            for k, v in value.items():
                week[key][k] = {}
                if prev_k:
                    week[key][k]['total'] = week[prev_k][k]['total'] + v
                    week[key][k]['percentage'] = float(
                        format((week[key][k]['total'] / (
                                col[key]['total'] + week[prev_k][k]['total_att'])
                                ) * 100, ".2f"))
                    week[key][k]['total_att'] = col[key]['total'] + week[prev_k][k][
                        'total_att']
                else:
                    week[key][k]['percentage'] = (v / col[key]['total']) * 100
                    week[key][k]['total'] = v
                    week[key][k]['total_att'] = col[key]['total']
            prev_k = key
            key_len += 1
        for keys, values in sorted(week.items()):
            for key, value in values.items(): # noqa
                if count >= len(st):
                    weekly_worksheet.write(student_row[key], col[keys]['col'] + 1,
                                           week[keys][key]['percentage'], no_format)
                else:
                    count += 1
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
                        cur_student = self.env['op.student'].search([(
                            'id', '=', i)])
                        pres.update({
                            cur_student.id: len(current_sheets)
                        })
                        weekly_worksheet.write(student_row[student.student_id.id],
                                               b + 1, pres[cur_student.id], no_format)
                        percentage = (pres[cur_student.id] / len(
                            total_lectures_taken)) * 100
                        weekly_worksheet.write(student_row[student.student_id.id],
                                               b, format(percentage, ".2f"), no_format)
                    ro += 1
                weekly_worksheet.write(student_row[student.student_id.id], b + 2,
                                       len(total_lectures_taken), no_format)
        weekly_worksheet.merge_range(0, b, 2, b, 'Total Attendance in Percentage(%)',
                                     header_format)
        weekly_worksheet.merge_range(0, b + 1, 2, b + 1, 'Total Lectures Attended',
                                     header_format)
        weekly_worksheet.merge_range(0, b + 2, 2, b + 2, 'Total Lectures Taken',
                                     header_format)
        workbook.close()
