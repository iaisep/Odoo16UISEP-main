# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################
import io
import json
import re

import xlsxwriter

from odoo import SUPERUSER_ID, _, http
from odoo.exceptions import AccessError, MissingError, UserError
from odoo.http import content_disposition, request
from odoo.tools import consteq

from odoo.addons.portal.controllers.portal import CustomerPortal


class GradeBook(CustomerPortal):
    @http.route(['/grading/excel_report/<model("grading.wizard"):wizard>',
                 ], type='http', auth="user")
    def grading_excel_report(self, wizard):
        response = request.make_response(
            None,
            headers=[
                ('Content-Type', 'application/vnd.ms-excel'),
                ('Content-Disposition', content_disposition(
                    'Grading_Assignment_Report' + '.xlsx'))
            ]
        )
        row = 5
        no = 1
        if wizard.course_id and wizard.academic_year_id:
            gradebooks = request.env['gradebook.gradebook'].search(
                [('course_id', '=', wizard.course_id.id),
                 ('academic_year_id', '=', wizard.academic_year_id.id)])
            output = io.BytesIO()
            workbook = xlsxwriter.Workbook(output, {'in_memory': True})
            no_format = workbook.add_format({
                'align': 'center'})
            header_format = workbook.add_format({
                'align': 'center', 'bold': True})
            analysis_format = workbook.add_format({'bold': True})
            rotate_format = workbook.add_format({
                'bold': True
            })
            r = 1
            assignment_count = []
            rotate_format.set_rotation(90)
            sheet = workbook.add_worksheet("Grading Assignment Report")
            sheet.write(0, 1, 'Course', header_format)
            sheet.write(1, 1, 'Semester', header_format)
            sheet.write(2, 1, 'Subject', header_format)
            sheet.write(3, 1, 'Subject Code', header_format)
            sheet.write(4, 0, 'Serial No.', header_format)
            sheet.write(4, 1, 'Student Name', header_format)
            sheet.set_column('A:A', 15)
            sheet.set_column('B:B', 25)
            sheet.set_column('C:K', 21)
            sheet.set_row(4, 150)
            summary_marks = {}
            avg_assign = {}
            if gradebooks:
                for gradebook in gradebooks:
                    cntr = 0
                    term = {}
                    subject = {}
                    for line in gradebook.gradebook_line_id:
                        if line.subject_id.name not in subject:
                            subject[line.subject_id.name] = 1
                        else:
                            count = subject[line.subject_id.name]
                            subject[line.subject_id.name] = count + 1

                        if line.academic_term_id.name not in term:
                            term[line.academic_term_id.name] = 1
                        else:
                            count = term[line.academic_term_id.name]
                            term[line.academic_term_id.name] = count + 1
                    sub = subject.copy()
                    sheet.write(row, 0, no, no_format)
                    sheet.write(row, 1, gradebook.student_id.name, no_format)
                    col = 2
                    marks = 0
                    m = 0
                    for line in gradebook.gradebook_line_id:
                        m += line.marks
                        summary_marks[gradebook.student_id.id] = m
                        if line.grade_assigment_id.id not in assignment_count:
                            assignment_count.append(line.grade_assigment_id.id)

                        if line.academic_term_id.name in term:
                            if term[line.academic_term_id.name] > 1:
                                sheet.merge_range(
                                    1, col, 1, col + term[line.academic_term_id.name],
                                    line.academic_term_id.name, header_format)
                                term[line.academic_term_id.name] = 0
                            elif term[line.academic_term_id.name] == 1:
                                sheet.merge_range(
                                    1, col, 1, col + 1, line.academic_term_id.name,
                                    header_format)

                        if line.subject_id.name in subject:
                            if subject[line.subject_id.name] > 1:
                                sheet.merge_range(
                                    2, col, 2, col + subject[line.subject_id.name],
                                    line.subject_id.name, header_format)
                                sheet.merge_range(
                                    3, col, 3, col + subject[line.subject_id.name],
                                    line.subject_id.code, header_format)
                                subject[line.subject_id.name] = 0
                            elif subject[line.subject_id.name] == 1:
                                sheet.write(2, col, line.subject_id.name,
                                            header_format)
                                sheet.write(3, col, line.subject_id.code,
                                            header_format)

                        sheet.write(4, col, line.grade_assigment_id.name,
                                    rotate_format)
                        sheet.write(row, col, line.marks, no_format)
                        col += 1
                        cnt = 0
                        avg1 = 0
                        if sub[line.subject_id.name] > 1 or \
                                sub[line.subject_id.name] == 0:
                            marks += line.marks
                            cntr += 1
                            if cntr:
                                avg1 = marks / cntr
                        if sub[line.subject_id.name] > 1:
                            sub[line.subject_id.name] = 0
                            col -= 1
                        elif sub[line.subject_id.name] == 0:
                            sheet.write(4, col, 'Average Marks', rotate_format)
                            sheet.write(row, col, avg1, no_format)
                            marks = 0
                            cntr = 0
                        else:
                            avg = 0
                            cnt += 1
                            if cnt:
                                avg = line.marks / cnt
                            sheet.write(4, col, 'Average Marks', rotate_format)
                            sheet.write(row, col, avg, no_format)
                        col += 1
                    sheet.merge_range(
                        0, r + 1, 0, r + len(assignment_count) + len(term),
                        wizard.course_id.name, header_format)
                    row += 1
                    no += 1
                column = 2
                assignment_count.clear()
                for gradebook in gradebooks:
                    for line in gradebook.gradebook_line_id:
                        if line.grade_assigment_id.id in avg_assign:
                            avg_assign[line.grade_assigment_id.id] = \
                                (avg_assign[line.grade_assigment_id.id] + line.marks) \
                                / len(gradebooks)
                        else:
                            avg_assign[line.grade_assigment_id.id] = line.marks
                        if line.grade_assigment_id.id not in assignment_count:
                            assignment_count.append(line.grade_assigment_id.id)
                            sheet.write(row + 2, column, line.grade_assigment_id.name,
                                        header_format)
                            column += 1
                sheet.write(row + 2, 0, "ANALYSIS", header_format)
                sheet.write(row + 3, 1, "Average Marks", analysis_format)
                c = 2
                for key, value in avg_assign.items(): # noqa
                    sheet.write(row + 3, c, avg_assign[key], no_format)
                    c += 1
            workbook.close()
            output.seek(0)
            response.stream.write(output.read())
            output.close()
        return response

    @http.route(['/grade-book', '/grade-book/<int:student_id>'],
                type="http", website=True, auth="user")
    def grade_book_view_portal(self, student_id=None, **kw):
        data = []
        user = request.env.user
        if not student_id:
            student_id = request.env['op.student'].sudo().search([
                ('user_id', '=', user.id)])
            student_progression_id = request.env['gradebook.gradebook'].sudo().search(
                [('student_id', '=', student_id.id)], limit=1)
        else:
            student_progression_id = request.env['gradebook.gradebook'].sudo().search(
                [('student_id', '=', student_id)], limit=1)

        data.append({
            'report': student_progression_id.get_unofficial_report_portal_url(
                report_type='pdf', download=True),
        })
        return request.render('openeducat_grading.grade_book_view_portal', {
            'student_progression_id': student_progression_id.id,
            'page_name': 'grade_book',
            'data': data
        })

    @http.route(['/get-grade-book/data'], type="json", website=True, auth="none")
    def get_grade_book_json_data(self, progression_id):
        student_progression = request.env['gradebook.gradebook'].sudo().search([
            ('id', '=', int(progression_id))])
        if student_progression.state == 'publish':
            if student_progression.gradebook:
                data = {}
                for i in student_progression.gradebook_line_id:
                    if i.course_id.grade_scale_id:
                        credit = True
                    else:
                        credit = False
                    break
                data[student_progression.student_id.name] = json.loads(
                    student_progression.gradebook)
                return {'data': json.dumps(data),
                        'credit': credit}
            else:
                return False
        else:
            return False

    def _document_check_access(self, model_name, document_id, access_token=None):
        document = request.env[model_name].browse([document_id])
        document_sudo = document.with_user(SUPERUSER_ID).exists()
        if not document_sudo:
            raise MissingError(_("This document does not exist."))
        try:
            document.check_access_rights('read')
            document.check_access_rule('read')
        except AccessError:
            if not access_token or not document_sudo.access_token or not consteq(
                    document_sudo.access_token, access_token):
                raise
        return document_sudo

    @http.route(['/grade-book/report/download/<int:student_id>'],
                type='http', auth="user", website=True)
    def portal_order_pages(self, student_id, report_type=None, access_token=None,
                           download=False, **kw):
        try:
            order_sudo = self._document_check_access('gradebook.gradebook', student_id,
                                                     access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/grade-book')

        if report_type in ('html', 'pdf', 'text'):
            return self._show_report(
                model=order_sudo, report_type=report_type,
                report_ref='openeducat_grading.action_report_gradebook',
                download=download)
        values = {
            'token': access_token,
            'partner_id': order_sudo.partner_id.id,
            'report_type': 'html',
        }

        return request.render('openeducat_grading.student_grade_report', values)

    def _show_report(self, model, report_type, report_ref, download=False):
        if report_type not in ('html', 'pdf', 'text'):
            raise UserError(_("Invalid report type: %s") % report_type)

        # report_sudo = request.env.ref(report_ref).sudo()
        report_sudo = request.env.ref(report_ref).with_user(SUPERUSER_ID)

        if hasattr(model, 'company_id'):
            report_sudo = report_sudo.with_company(model.company_id)

        if not isinstance(report_sudo, type(request.env['ir.actions.report'])):
            raise UserError(
                _("%s is not the reference of a report") % report_ref)

        method_name = '_render_qweb_%s' % (report_type)
        report = getattr(report_sudo, method_name)(
            report_ref, list(model.ids), data={'report_type': report_type})[0]
        reporthttpheaders = [
            ('Content-Type',
             'application/pdf' if report_type == 'pdf' else 'text/html'),
            ('Content-Length', len(report)),
        ]
        if report_type == 'pdf' and download:
            filename = "%s.pdf" % (re.sub(r'\W+', '-',
                                          model._get_report_base_filename()))
            reporthttpheaders.append(('Content-Disposition',
                                      content_disposition(filename)))
        return request.make_response(report, headers=reporthttpheaders)
