# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

import json
import math
import uuid
from collections import Counter

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class GradebookGradebook(models.Model):
    _name = 'gradebook.gradebook'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Grade Book"
    _rec_name = "student_id"

    name = fields.Char(string='Name',
                       required=True, copy=False, readonly=True,
                       index=True, default=lambda self: _('New'))
    student_id = fields.Many2one('op.student', string="Student", required=True)
    gradebook_line_id = fields.One2many('gradebook.line', 'gradebook_id',
                                        string='Gradebook Line')
    gradebook = fields.Char(string="Gradebook")
    percentage = fields.Float(string="Percentage")
    grade = fields.Char(string="Grade", store=True)
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'), ('inprogress', 'In Progress'),
            ('publish', 'Publish'), ('cancelled', 'Cancelled')
        ], default='draft', tracking=True
    )
    academic_year_ids = fields.Many2one('op.academic.year', string='Academic Year',
                                        tracking=True)
    course_id = fields.Many2one('op.course', string='Course',
                                tracking=True, required=True)
    grade_override = fields.One2many('op.grade.override.line',
                                     'grade_grade_id', string='Final Grades',
                                     tracking=True)
    override_hide = fields.Boolean('Override Hide')
    academic_year_id = fields.Many2many('op.academic.year', string='Year',
                                        required=True, tracking=True)
    report_access_url = fields.Char(
        'Portal Access URL Report', compute='_compute_report_access_url',
        help='Customer Portal URL')
    access_token = fields.Char('Security Token', copy=False)
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)
    report_type = fields.Selection([('single', 'Single Column'),
                                    ('double', 'Two Column')],
                                   default='double', string='Report Type')

    def _compute_report_access_url(self):
        for record in self:
            record.report_access_url = '/grade-book/report/download/%s' % (record.id)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', '/') == '/':
                vals['name'] = self.env['ir.sequence'].\
                    next_by_code('gradebook.gradebook') or '/'
        return super(GradebookGradebook, self).create(vals_list)

    # @api.onchange('gradebook_line_id')
    def calculate_percentage(self):
        template = self.env['op.grade.template'].search([])
        courses = self.env['op.course'].search([('id', 'in',
                                                 self.student_id.course_detail_ids.
                                                 course_id.ids)])
        term_lst = {}
        year_dict = {}
        sem_dict = {}
        for record in self.gradebook_line_id:
            term_lst.update({record.academic_year_id.name: {}})

        for key in term_lst:
            for record in self.gradebook_line_id:
                if record.academic_term_id.parent_term:
                    if key == record.academic_year_id.name:
                        year_dict.update({record.academic_term_id.parent_term.name: {},
                                          'Year Total': {}, 'Grade': {}})
                        Quarter_term = True
                else:
                    if key == record.academic_year_id.name:
                        year_dict.update({record.academic_term_id.name: {},
                                          'Year Total': {}, 'Grade': {}})
                        Quarter_term = False
            term_lst.update({key: year_dict})
            year_dict = {}

        for key, value in term_lst.items():
            for res in value:
                for record in self.gradebook_line_id:
                    if record.academic_term_id.parent_term:
                        if key == record.academic_year_id.name:
                            if res == record.academic_term_id.parent_term.name:
                                sem_dict.update({record.academic_term_id.name: {}})
                value[res] = sem_dict
                sem_dict = {}
        sub_count = {}
        sub_weightage = {}
        new_count = {}
        academic_count = {}
        lst = []
        temp_academic_count = {}

        for key, value in term_lst.items():
            for key1, value1 in value.items():
                if value1:
                    for temp in value1:
                        for course in courses:
                            for subject in course.subject_ids:
                                if not subject.default_template:
                                    for grade_template in subject.grade_template_ids:
                                        for template_line in grade_template. \
                                                template_line_ids:
                                            for record in self.gradebook_line_id:
                                                if record.academic_term_id.parent_term:
                                                    if key == record.academic_year_id.\
                                                            name:
                                                        if key1 == record.\
                                                                academic_term_id.\
                                                                parent_term.name:
                                                            if course == record.\
                                                                    course_id:
                                                                if subject.\
                                                                        id == record.\
                                                                        subject_id.id:
                                                                    if template_line. \
                                                                            academic_term_id.id == record.academic_term_id.id:  # noqa
                                                                        if temp == record.academic_term_id.name:  # noqa
                                                                            if record.grade_assigment_id.active: # noqa
                                                                                lst.\
                                                                                    append(record.assignment_type_id.name)  # noqa
                                    type_count = Counter(lst)
                                    if type_count:
                                        sub_count.update({subject.name: type_count})
                                    lst = []
                                else:
                                    for grade_template in course.grade_template_ids:
                                        for template_line in grade_template. \
                                                template_line_ids:
                                            for record in self.gradebook_line_id:
                                                if subject.id == record.subject_id.id:
                                                    if record.academic_term_id.\
                                                            parent_term:
                                                        if key == record.\
                                                                academic_year_id.name:
                                                            if key1 == record.\
                                                                    academic_term_id.\
                                                                    parent_term.name:
                                                                if course == record.\
                                                                        course_id:
                                                                    if template_line.academic_term_id.id == record.academic_term_id.id:  # noqa
                                                                        if temp == record.academic_term_id.name:  # noqa
                                                                            if record.grade_assigment_id.active: # noqa
                                                                                lst. \
                                                                                    append(record.assignment_type_id.name)  # noqa
                                    if lst:
                                        type_count = Counter(lst)
                                        sub_count.update({subject.name: type_count})
                                    lst = []
                        temp_academic_count.update({temp: sub_count})
                        sub_count = {}
                    new_count.update({key1: temp_academic_count})
                    temp_academic_count = {}
                else:
                    for course in courses:
                        for subject in course.subject_ids:
                            if not subject.default_template:
                                for grade_template in subject.grade_template_ids:
                                    for template_line in grade_template.\
                                            template_line_ids:
                                        for record in self.gradebook_line_id:
                                            if key == record.academic_year_id.name:
                                                if key1 == record.academic_term_id.name:
                                                    if course == record.course_id:
                                                        if subject.id == record.\
                                                                subject_id.id:
                                                            if template_line.\
                                                                    academic_term_id.\
                                                                    id == record.\
                                                                    academic_term_id.\
                                                                    id:
                                                                if record.grade_assigment_id.active: # noqa
                                                                    lst. \
                                                                        append(record.assignment_type_id.name) # noqa

                                type_count = Counter(lst)
                                if type_count:
                                    sub_count.update({subject.name: type_count})
                                lst = []
                                type_count = ''
                            else:
                                for grade_template in course.grade_template_ids:
                                    for template_line in grade_template.\
                                            template_line_ids:
                                        for record in self.gradebook_line_id:
                                            if key == record.academic_year_id.name:
                                                if key1 == record.academic_term_id.name:
                                                    if course == record.course_id:
                                                        if subject.id == record.\
                                                                subject_id.id:
                                                            if template_line.\
                                                                    academic_term_id.\
                                                                    id == record.\
                                                                    academic_term_id.\
                                                                    id:
                                                                if record.grade_assigment_id.active: # noqa
                                                                    lst.append(
                                                                        record.assignment_type_id.name) # noqa
                                if lst:
                                    type_count = Counter(lst)
                                    sub_count.update({subject.name: type_count})
                                lst = []
                    new_count.update({key1: sub_count})
                    sub_count = {}
            academic_count.update({key: new_count})
            new_count = {}

        weightage_dict = {}
        new_weighage = {}
        temp_dict = {}
        subterm_dict = {}
        sums = []
        subject_detail = {}

        for key, value in term_lst.items():
            for key1, value1 in value.items():
                if value1:
                    for temp in value1:
                        for course in courses:
                            for subject in course.subject_ids:
                                if not subject.default_template:
                                    for grade_template in subject.grade_template_ids:
                                        for record in self.gradebook_line_id:
                                            if subject.id == record.subject_id.id:
                                                for template_line in grade_template. \
                                                        template_line_ids:
                                                    if template_line.\
                                                            academic_term_id.\
                                                            id == record.\
                                                            academic_term_id.id:
                                                        if temp == record.academic_term_id.name:  # noqa
                                                            if key == record.\
                                                                    academic_year_id.\
                                                                    name:
                                                                if key1 == record.academic_term_id.parent_term.name: # noqa
                                                                    for weightage in \
                                                                            template_line.assignment_type_weight_ids:  # noqa
                                                                        if record.assignment_type_id == weightage.assignment_type_id:  # noqa
                                                                            if record.grade_assigment_id.active: # noqa
                                                                                sub_weightage.update({record.assignment_type_id.name: weightage.weightage / float( # noqa
                                                                                    academic_count[record.academic_year_id.name][record.academic_term_id. # noqa
                                                                                        parent_term.name][record.academic_term_id.name][record.subject_id. # noqa
                                                                                        name][record.assignment_type_id.name])})  # noqa
                                    if sub_weightage:
                                        subterm_dict.update(
                                            {subject.name: sub_weightage})
                                        sub_weightage = {}
                                else:
                                    for grade_template in course.grade_template_ids:
                                        for record in self.gradebook_line_id:
                                            if subject.id == record.subject_id.id:
                                                for template_line in grade_template. \
                                                        template_line_ids:
                                                    if template_line.\
                                                            academic_term_id.\
                                                            id == record.\
                                                            academic_term_id.id:
                                                        if temp == record. \
                                                                academic_term_id.name:
                                                            if key == record.\
                                                                    academic_year_id.\
                                                                    name:
                                                                if key1 == record.academic_term_id.parent_term.name: # noqa
                                                                    for weightage in \
                                                                            template_line.assignment_type_weight_ids:  # noqa
                                                                        if record.assignment_type_id == weightage.assignment_type_id:  # noqa
                                                                            if record.grade_assigment_id.active: # noqa
                                                                                sub_weightage.update({record.assignment_type_id.name: weightage.weightage / float( # noqa
                                                                                        academic_count[record.academic_year_id.name][record.academic_term_id. # noqa
                                                                                            parent_term.name][record.academic_term_id.name][record.subject_id. # noqa
                                                                                            name][record.assignment_type_id.name])})  # noqa
                                    if sub_weightage:
                                        subterm_dict.update(
                                            {subject.name: sub_weightage})
                                        sub_weightage = {}

                        temp_dict.update({temp: subterm_dict})
                        subterm_dict = {}

                    new_weighage.update({key1: temp_dict})
                    temp_dict = {}
                else:
                    for course in courses:
                        for subject in course.subject_ids:
                            if not subject.default_template:
                                for grade_template in subject.grade_template_ids:
                                    for record in self.gradebook_line_id:
                                        if subject.id == record.subject_id.id:
                                            for template_line in grade_template. \
                                                    template_line_ids:
                                                if template_line.academic_term_id.\
                                                        id == record.\
                                                        academic_term_id.id:
                                                    for weightage in template_line. \
                                                            assignment_type_weight_ids:
                                                        if key == record.\
                                                                academic_year_id.\
                                                                name:
                                                            if key1 == record.\
                                                                    academic_term_id.\
                                                                    name:
                                                                if record.\
                                                                        assignment_type_id == weightage.assignment_type_id: # noqa
                                                                    if record.grade_assigment_id.active: # noqa
                                                                        sub_weightage.\
                                                                            update({record.assignment_type_id.name: weightage.weightage / float( # noqa
                                                                                    academic_count[record.academic_year_id.name][record.academic_term_id. # noqa
                                                                                        name][record.subject_id.name][record.assignment_type_id.name])})  # noqa
                                temp_dict.update({subject.name: sub_weightage})
                                sub_weightage = {}
                            else:
                                for grade_template in course.grade_template_ids:
                                    for template_line in grade_template.\
                                            template_line_ids:
                                        for record in self.gradebook_line_id:
                                            if key == record.academic_year_id.name:
                                                if key1 == record.academic_term_id.name:
                                                    if course == record.course_id:
                                                        if subject.id == record. \
                                                                subject_id.id:
                                                            if template_line. \
                                                                    academic_term_id.\
                                                                    id \
                                                                    == record. \
                                                                    academic_term_id.id:
                                                                for weightage in template_line.assignment_type_weight_ids:  # noqa
                                                                    if record.assignment_type_id == weightage.assignment_type_id: # noqa
                                                                        if record.grade_assigment_id.active: # noqa
                                                                            sub_weightage.update({record.assignment_type_id.name: weightage.weightage / float( # noqa
                                                                                academic_count[record.academic_year_id.name][record.academic_term_id.name][record. # noqa
                                                                                    subject_id.name][record.assignment_type_id.name])})  # noqa
                                if sub_weightage:
                                    temp_dict.update({subject.name: sub_weightage})
                                    sub_weightage = {}
                    new_weighage.update({key1: temp_dict})
                    temp_dict = {}
            weightage_dict.update({key: new_weighage})
            new_weighage = {}
        subtotal = []
        subterm_total = []
        subterm_dict_2 = {}
        subject_mark = {}
        final_total = []
        final_totals = []
        sums_total = []
        sem_total = {}
        sum_weightage = []
        year_total = []
        sum_weight = []
        average_quarter = []
        sub_weightage = []
        sumss_total = []
        all_assigment = {}
        all_assigment_1 = {}
        value_dict = {}
        academic_total = []
        all_total = []
        for key, value in term_lst.items():
            for key1, value1 in value.items():
                if value1:
                    try:
                        for temp in value1:
                            for course in courses:
                                for subject in course.subject_ids:
                                    for record in self.gradebook_line_id:
                                        if subject.id == record.subject_id.id:
                                            if temp == record.academic_term_id.name:
                                                if key == record.academic_year_id.name:
                                                    if record.academic_term_id.\
                                                            parent_term:
                                                        if record.grade_assigment_id.\
                                                                active:
                                                            try:
                                                                calc = record.percentage * (weightage_dict[record.academic_year_id.name][record.academic_term_id.parent_term.name][ # noqa
                                                                                                record.academic_term_id.name][ # noqa
                                                                                                record.subject_id.name][ # noqa
                                                                                                record.assignment_type_id.name] * 100 / 100)  # noqa
                                                                sum_weightage. \
                                                                    append(weightage_dict[record.academic_year_id.name][record.academic_term_id.parent_term. # noqa
                                                                           name][record.academic_term_id.name][record.subject_id.name][record.assignment_type_id. # noqa
                                                                           name])
                                                                if not course.\
                                                                        grade_scale_id.op_grade_type_ids: # noqa
                                                                    all_assigment.\
                                                                        update({record.grade_assigment_id.name: "{:0.2f}".format(record.percentage)})  # noqa
                                                                else:
                                                                    for scale in course.grade_scale_id.op_grade_type_ids: # noqa
                                                                        if (record.percentage >= scale.min_percentage) and (record.percentage <= scale.max_percentage):  # noqa
                                                                            grade = scale.name # noqa
                                                                            all_assigment.update({record.grade_assigment_id.name: { # noqa
                                                                                'Mark': "{:0.2f}".format(record.percentage), # noqa
                                                                                'Grade': grade}}) # noqa
                                                                calc_1 = (calc / 100)
                                                                sums.append(calc_1)
                                                                sumss_total.\
                                                                    append(calc_1)
                                                            except Exception:
                                                                raise ValidationError(_(
                                                                    'Please Recheck'
                                                                    ' Your Template'
                                                                    ' Configuration'))
                                    if sums:
                                        final_totals.append(sum(sums) * 100 / sum(
                                            sum_weightage))
                                        marks = (sum(sums) * 100 / sum(sum_weightage))

                                        sums_total. \
                                            append(sum(sums) / len(sums) * 100 / sum(sum_weightage)) # noqa
                                        if not course.grade_scale_id.op_grade_type_ids:
                                            subject_detail.update(
                                                {'Assignment': all_assigment,
                                                 'Mark': "{:0.2f}".format(marks),
                                                 'Code': subject.code})
                                        else:
                                            for scale in course.grade_scale_id. \
                                                    op_grade_type_ids:
                                                if (marks >= scale.min_percentage) and (
                                                        marks <= scale.max_percentage):  # noqa
                                                    grade = scale.name
                                                    if scale.earn_credits:
                                                        credit = subject.credit_point
                                                    else:
                                                        credit = 0.0
                                                    subject_detail.update(
                                                        {'Assignment': all_assigment,
                                                         'Mark': "{:0.2f}".format(
                                                             marks),
                                                         'Grade': grade,
                                                         'Credit': credit,
                                                         'Code': subject.code})
                                        subject_mark.update(
                                            {subject.name: subject_detail})
                                        sums = []
                                        sum_weight.append(sum(sum_weightage))
                                        sum_weightage = []
                                        all_assigment = {}
                                        subject_detail = {}
                            for course in courses:
                                for record in self.gradebook_line_id:
                                    if course.id == record.course_id.id:
                                        quarter_mark = (sum(final_totals) / len(final_totals))  # noqa
                                        if course.grade_scale_id.op_grade_type_ids:
                                            for scale in course.grade_scale_id.op_grade_type_ids:  # noqa
                                                if (quarter_mark >= scale.min_percentage) and (  # noqa
                                                        quarter_mark <= scale.max_percentage):  # noqa
                                                    grade = scale.name
                                                    subject_mark.update(
                                                        {'Grade': grade,
                                                         'Total': "{:0.2f}".format(quarter_mark)})  # noqa
                                        else:
                                            subject_mark.update({'Total': "{:0.2f}".format(quarter_mark)})  # noqa
                                        average_quarter.append(sum(final_totals) / len(final_totals))  # noqa
                            for course in courses:
                                # for record in self.gradebook_line_id:
                                #     if course.id == record.course_id.id:
                                for template in course.grade_template_ids:
                                    for template_line in template.template_line_ids:
                                        if template_line.weightage == 'sub_term':
                                            if key == template_line.academic_years_id.\
                                                    name:
                                                if key1 == template_line.\
                                                        academic_term_id.name:
                                                    for subterm_weight in template_line.subterm_weight_ids: # noqa
                                                        if temp == subterm_weight. \
                                                                academic_sub_term_id.\
                                                                name:
                                                            subterm_total.append(((sum(final_totals) / len(  # noqa
                                                                final_totals)) * subterm_weight.weightage) / 100)  # noqa
                                                            sub_weightage.append(subterm_weight.weightage)  # noqa
                                subterm_dict_2.update({temp: subject_mark})
                            final_totals = []
                            sums_total = []
                            subject_mark = {}
                            if sub_weightage:
                                total_marks = (sum(subterm_total))
                            else:
                                total_marks = (sum(average_quarter) / len(
                                    average_quarter))
                            year_total.append(total_marks)
                            for course in courses:
                                for record in self.gradebook_line_id:
                                    if course.id == record.course_id.id:
                                        overall_sem = sum(year_total) / len(year_total)
                                        if course.grade_scale_id.op_grade_type_ids:
                                            for scale in course.grade_scale_id.op_grade_type_ids:  # noqa
                                                if (overall_sem >= scale.
                                                        min_percentage) and (
                                                        overall_sem <= scale.
                                                        max_percentage):
                                                    grade = scale.name
                                                    if scale.form_factor:
                                                        gpa = float("{:0.2f}".format(
                                                            overall_sem)) / scale.\
                                                            factor
                                                    else:
                                                        gpa = scale.gpa_value
                                                    subterm_dict_2.\
                                                        update(
                                                            {'Total': "{:0.2f}".format(
                                                                overall_sem),
                                                             'Grade': grade,
                                                             'GPA': "{:0.2f}".format(
                                                                 gpa)})
                                        else:
                                            subterm_dict_2.update(
                                                {'Total': "{:0.2f}".format(sum(
                                                    year_total) / len(year_total))})
                            # year_total.append(total_marks)
                            average_quarter = []
                        subterm_total = []
                        sum_weight = []
                        sub_weightage = []

                    except ZeroDivisionError:
                        pass
                else:
                    for course in courses:
                        for subject in course.subject_ids:
                            for record in self.gradebook_line_id:
                                if subject.id == record.subject_id.id:
                                    if record.grade_assigment_id.active:
                                        try:
                                            if key == record.academic_year_id.name:
                                                if key1 == record.academic_term_id.name:
                                                    calc = record.\
                                                               percentage * (weightage_dict[record.academic_year_id.name][record.academic_term_id. # noqa
                                                                name][record.subject_id.name][record.assignment_type_id.name] * 100 / 100) # noqa
                                                    calc_1 = (calc / 100)
                                                    sums.append(calc_1)
                                                    sum_weightage.\
                                                        append(weightage_dict[record.academic_year_id. # noqa
                                                               name][record.academic_term_id.name][record. # noqa
                                                               subject_id.name][record.assignment_type_id.name]) # noqa
                                                    if not course.grade_scale_id.\
                                                            op_grade_type_ids:
                                                        all_assigment_1.update(
                                                            {record.grade_assigment_id.name: "{:0.2f}".format(record.percentage)})  # noqa
                                                    else:
                                                        for scale in course.\
                                                                grade_scale_id.\
                                                                op_grade_type_ids:
                                                            if (record.percentage >= scale.min_percentage) and (record.percentage <= scale.max_percentage):  # noqa
                                                                grade = scale.name
                                                                all_assigment_1.update({
                                                                    record.grade_assigment_id.name: { # noqa
                                                                        'Mark': "{:0.2f}".format(record.percentage), # noqa
                                                                        'Grade': grade}}) # noqa
                                        except Exception:
                                            raise ValidationError(_(
                                                'Please Recheck Your '
                                                'Template Configuration'))
                            if sums:
                                final_total.append(sum(sums) * 100 / sum(sum_weightage))
                                if not course.grade_scale_id.op_grade_type_ids:
                                    subject_detail.update(
                                        {'Assignment': all_assigment_1,
                                         'Mark': "{:0.2f}".format(sum(sums) * 100 / sum(sum_weightage)),  # noqa
                                         'Code': subject.code,
                                         'Comment': '',
                                         'override': ''})
                                else:
                                    for scale in course.grade_scale_id.\
                                            op_grade_type_ids:
                                        if (math.ceil(sum(sums)) >= scale.
                                                min_percentage) and (
                                                math.ceil(sum(sums)) <= scale.max_percentage):  # noqa
                                            grade = scale.name
                                            if scale.earn_credits:
                                                credit = subject.credit_point
                                            else:
                                                credit = 0.0
                                            subject_detail.update(
                                                {'Assignment': all_assigment_1,
                                                 'Mark': "{:0.2f}".format(sum(sums) * 100 / sum(sum_weightage)),  # noqa
                                                 'Grade': grade,
                                                 'Credit': credit,
                                                 'Code': subject.code,
                                                 'Comment': '',
                                                 'override': ''})
                                subject_mark.update({subject.name: subject_detail})
                                subject_detail = {}
                                sums = []
                                sum_weightage = []
                                all_assigment_1 = {}

                if value1:
                    try:
                        for key2, value2 in subterm_dict_2.items(): # noqa
                            subtotal.append(value2)
                        term_lst[key][key1] = subterm_dict_2
                        value_dict = value.copy()
                        academic_total.append(sum(year_total) / len(year_total))
                        end = sum(academic_total) / len(academic_total)
                        for course in courses:
                            if not course.grade_scale_id.op_grade_type_ids:
                                value_dict['Year Total'] = "{:0.2f}".format(end)
                            else:
                                for scale in course.grade_scale_id.op_grade_type_ids:
                                    if (end >= scale.min_percentage) and (
                                            end <= scale.max_percentage):  # noqa
                                        grades = scale.name
                                        value_dict['Year Total'] = "{:0.2f}".format(end)
                                        value_dict['Grade'] = grades
                        sums = []
                        subtotal = []
                        subterm_total = []
                        subterm_dict_2 = {}
                    except ZeroDivisionError:
                        pass
                else:
                    try:
                        total_mark = sum(final_total) / len(final_total)
                        year_total.append(total_mark)
                        for course in courses:
                            if not course.grade_scale_id.op_grade_type_ids:
                                sem_total.update({'Total': "{:0.2f}".format(total_mark),
                                                  'Comment': '',
                                                  'Attendance': '',
                                                  'override': ''})
                            else:
                                for scale in course.grade_scale_id.op_grade_type_ids:
                                    if (math.ceil(total_mark) >= scale.min_percentage) and (math.ceil(total_mark) <= scale.max_percentage):  # noqa
                                        if scale.form_factor:
                                            gpa = float("{:0.2f}".
                                                        format(total_mark)) / scale.\
                                                factor
                                        else:
                                            gpa = scale.gpa_value
                                        grade = scale.name
                                        sem_total.update({'Total': "{:0.2f}".format(total_mark),  # noqa
                                                          'Grade': grade,
                                                          'GPA': gpa,
                                                          'Comment': '',
                                                          'Attendance': '',
                                                          'override': ''})
                        subject_mark.update(sem_total)
                        sem_total = {}
                        term_lst[key][key1] = subject_mark
                        value_dict = value.copy()
                        year_totals = ((sum(year_total)) / (len(year_total)))
                        academic_total.append(year_totals)
                        for course in courses:
                            if not course.grade_scale_id.op_grade_type_ids:
                                value_dict['Year Total'] = "{:0.2f}".\
                                    format(sum(academic_total) / len(academic_total))
                            else:
                                for scale in course.grade_scale_id.op_grade_type_ids:
                                    if (math.ceil(sum(academic_total) / len(
                                            academic_total)) >= scale.min_percentage
                                        ) and (math.ceil(sum(academic_total) / len(
                                            academic_total)) <= scale.max_percentage):
                                        grades = scale.name
                                        value_dict['Year Total'] = "{:0.2f}".\
                                            format(sum(academic_total) / len(
                                                academic_total))
                                        value_dict['Grade'] = grades
                        sums = []
                        final_total = []
                        subject_mark = {}
                    except ZeroDivisionError:
                        pass
                year_total = []
            all_mark = sum(academic_total) / len(academic_total)
            all_total.append(all_mark)
            for course in courses:
                if not course.grade_scale_id.op_grade_type_ids:
                    self.percentage = "{:0.2f}".format(sum(all_total) / len(all_total))
                else:
                    for scale in course.grade_scale_id.op_grade_type_ids:
                        if (math.ceil(sum(all_total) / len(all_total)) >= scale.
                                min_percentage) and (
                                math.ceil(sum(all_total) / len(all_total)) <= scale.max_percentage):  # noqa
                            self.percentage = "{:0.2f}".\
                                format(sum(all_total) / len(all_total))
                            self.grade = scale.name
            academic_total = []

            term_lst[key] = value_dict
        students = self.env['op.student.progression'].search([])
        if term_lst:
            term_lst['Quarter_term'] = Quarter_term
            for rec in self:
                rec.gradebook = json.dumps(term_lst, indent=4)
            for student in students:
                if student.student_id == self.student_id:
                    student.grade_book = json.dumps(term_lst, indent=4)
            return term_lst

    def calculate_attendance(self):
        dates = []
        courses = self.env['op.course'].search([('id', 'in', self.student_id.
                                                 course_detail_ids.course_id.ids)])
        attendance = self.env['op.attendance.sheet'].search([('state', '=', 'done')])
        for date in attendance:
            dates.append(str(date.attendance_date))
        days = list(dict.fromkeys(dates))
        day_to_day = []
        temp_date = []
        everyday_sheet = []
        attendance_total = []
        dictionary = self.calculate_percentage()
        for record in self.gradebook_line_id:
            if record.assignment_type_id.assign_type == 'attendance':
                for key, value in dictionary.items():
                    for key1, value1 in value.items():
                        if type(value1) is str or type(value1) is float:
                            pass
                        else:
                            for key2, value2 in value1.items():
                                if type(value2) is float:
                                    pass
                                else:
                                    for i in days:
                                        if str(record.academic_term_id.term_start_date) <= i <= str(record.academic_term_id.term_end_date): # noqa
                                            if i not in temp_date:
                                                temp_date.append(i)
                                                present = self.env[
                                                    'op.attendance.line'].search_count(
                                                    [('attendance_id', 'in',
                                                      attendance.ids),
                                                     ('course_id', '=', record.
                                                      course_id.name),
                                                     ('student_id', "=", self.
                                                      student_id.id),
                                                     ('present', '=', True),
                                                     (str('attendance_date'), '=',
                                                      i)])
                                                # late = self.env[
                                                # 'op.attendance.line'].search_count(
                                                # [('attendance_id', 'in',
                                                # attendance.ids),
                                                #      ('course_id', '=',
                                                #      record.course_id.name),
                                                #      ('student_id', "=",
                                                #      self.student_id.id),
                                                #      ('late', '=', True),
                                                #      (str('attendance_date'), '=',
                                                #      i)])
                                                excuse = self.env[
                                                    'op.attendance.line'].search_count(
                                                    [('attendance_id', 'in',
                                                      attendance.ids),
                                                     ('course_id', '=', record.
                                                      course_id.name),
                                                     ('student_id', "=", self.
                                                      student_id.id),
                                                     ('excused', '=', True),
                                                     (str('attendance_date'),
                                                      '=', i)])
                                                absent = self.env[
                                                    'op.attendance.line'].\
                                                    search_count([
                                                        ('attendance_id', 'in',
                                                         attendance.ids),
                                                        ('course_id', '=', record.
                                                         course_id.name),
                                                        ('student_id', "=", self.
                                                         student_id.id),
                                                        ('present', '!=', True),
                                                        ('excused', '!=', True),
                                                        (str('attendance_date'), '=',
                                                         i)])
                                                for course in courses:
                                                    if course.id == record.course_id.id:
                                                        for template in course. \
                                                                grade_template_ids:
                                                            for template_line in template.template_line_ids: # noqa
                                                                if template_line.\
                                                                        weightage == 'attendance_type': # noqa
                                                                    for subterm_weight in template_line.attendance_type_weight_ids:  # noqa
                                                                        if subterm_weight.attendance_type == 'present':  # noqa
                                                                            attendance_total.append(present * subterm_weight.weightage)  # noqa
                                                                        # if subterm_weight.attendance_type == 'late': # noqa
                                                                        #     attendance_total.append(late * subterm_weight.weightage) # noqa
                                                                        if subterm_weight.attendance_type == 'excuse':  # noqa
                                                                            attendance_total.append(excuse * subterm_weight.weightage)  # noqa
                                                                        if subterm_weight.attendance_type == 'absent':  # noqa
                                                                            attendance_total.append(absent * subterm_weight.weightage)  # noqa
                                                total = (sum(attendance_total)) / (
                                                    present + excuse + absent)
                                                day_to_day.append(total)
                                                attendance_total = []
                                    if day_to_day:
                                        total_days = (sum(day_to_day) / len(day_to_day))
                                        everyday_sheet.append(total_days)
                                        day_to_day = []

                                if key == record.academic_year_id.name:
                                    if key2 == record.academic_term_id.name:
                                        value2['Attendance'] = "{:0.2f}".format(sum(
                                            everyday_sheet))
                                        everyday_sheet = []
                            if key == record.academic_year_id.name:
                                if key1 == record.academic_term_id.name:
                                    value1.update({'Attendance': "{:0.2f}".format(sum(
                                        everyday_sheet))})
                                    everyday_sheet = []
                students = self.env['op.student.progression'].search([])
                if dictionary:
                    self.gradebook = json.dumps(dictionary, indent=4)
                    for student in students:
                        if student.student_id == self.student_id:
                            student.grade_book = json.dumps(dictionary, indent=4)

    @api.onchange('gradebook_line_id')
    def calculation_main(self):
        if self.state == 'publish':
            self.calculate_percentage()
            self.calculate_attendance()

    def action_view_gradebook(self):
        action = self.env.ref('openeducat_student_progress_enterprise.'
                              'grade_book_action_window').read()[0]
        action['domain'] = [('student_id', "=", self.student_id)]

        value = {
            'name': 'GradeBoook',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'op.student.progression',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'current',
        }
        return value

    def open_grade_book_grid(self):
        self.ensure_one()
        value = {
            'type': 'ir.actions.client',
            'name': _('GradeBook'),
            'tag': 'grade_book_grade_book_grid',
            'target': 'current',
            'params': {'grade_book': self.id},
            'domain': [('student_id', "=", self.student_id.id)],
            'params': {'grade_book': self.student_id.id, 'is_gradebook': self.id},
        }
        return value

    def get_grade_book_grid_data(self, student_id=None, is_gradebook=False):
        data = {}
        domain = [('student_id', '=', int(student_id)), ('state', '=', 'publish')]
        if is_gradebook:
            domain += [('id', '=', int(is_gradebook))]
        progression = self.env['gradebook.gradebook'].search(domain)
        for p in progression:
            if p.gradebook:
                data[p.course_id.name] = json.loads(p.gradebook)
        return {'data': json.dumps(data)}

    def get_all_student_grade_data(self):
        data = []
        gradebook = self.env['gradebook.gradebook'].search([])
        for grade in gradebook:
            if grade.gradebook:
                for i in grade.gradebook_line_id:
                    subData = {}
                    if i.course_id.grade_scale_id:
                        credit = True
                    else:
                        credit = False
                    subData[grade.student_id.name] = json.loads(grade.gradebook)
                    break
                data.append({
                    'data': json.dumps(subData),
                    'credit': credit,
                    'name': grade.student_id.name,
                })
        return data

    def action_draft(self):
        for obj in self:
            obj.state = 'draft'
        return True

    def action_inprogress(self):
        for obj in self:
            obj.state = 'inprogress'
        return True

    def action_publish(self):
        for obj in self:
            obj.state = 'publish'
        self.calculate_percentage()
        self.calculate_attendance()
        return True

    def action_cancelled(self):
        for obj in self:
            obj.state = 'cancelled'
        return True

    @api.onchange('percentage')
    def calculate_total_year(self):
        courses = self.env['op.course'].search([('id', 'in',
                                                 self.student_id.course_detail_ids.
                                                 course_id.ids)])
        if self.gradebook:
            gradebooks = json.loads(self.gradebook)
            for course in courses:
                if not course.grade_scale_id.op_grade_type_ids:
                    gradebooks['override'] = self.percentage
                else:
                    for scale in course.grade_scale_id.op_grade_type_ids:
                        if (self.percentage >= scale.min_percentage) and (
                                self.percentage <= scale.max_percentage):  # noqa
                            grade = scale.name
                            gradebooks['override'] = self.percentage
                            gradebooks['Grade'] = grade
                            self.grade = gradebooks['Grade']
            self.gradebook = json.dumps(gradebooks, indent=4)

    def student_Grade_override(self):
        self.override_hide = True
        subject = self.env['op.subject'].sudo().search([])
        if self.student_id:
            terms = json.loads(self.gradebook)
            for res in self.academic_year_id:
                for key, value in terms.items():
                    if type(value) != bool:
                        for key1, value1 in value.items():
                            if key == res.name:
                                for rec in res.academic_term_ids:
                                    if key1 == rec.name:
                                        self.write({
                                            'grade_override': [(0, 0, {
                                                'year': res.id,
                                                'term': rec.id,
                                                'calculated': value1['Total'] if 'Total' in value1 else None, # noqa
                                                'grade': value1['Grade'] if 'Grade' in value1 else None,  # noqa
                                                'final': value1['Grade'] if 'Grade' in value1 else None  # noqa
                                            })]
                                        })
                                if type(value1) is str or type(value1) is float:
                                    pass
                                else:
                                    for temp, values in value1.items():
                                        ter = self.env['op.academic.term'].search([
                                            ('name', '=', temp),
                                            ('academic_year_id', '=', res.id)])
                                        for rec in res.academic_term_ids:
                                            if key == res.name:
                                                if temp == rec.name:
                                                    self.write({
                                                        'grade_override': [(0, 0, {
                                                            'term': rec.id,
                                                            'calculated': value1[temp][
                                                                'Total'],
                                                            'grade': value1[temp]['Grade'] if 'Grade' in value1[temp] else None, # noqa
                                                            'final': value1[temp]['Grade'] if 'Grade' in value1[temp] else None # noqa
                                                        })]
                                                    })
                                        if type(values) is str or type(values) is float:
                                            pass
                                        else:
                                            for sub in values or []:
                                                for rec in subject:
                                                    if sub == rec.name:
                                                        self.write({
                                                            'grade_override': [
                                                                (0, 0, {
                                                                    # 'year': key,
                                                                    'term': ter.id,
                                                                    'subject': rec.id,
                                                                    'calculated': values[sub]['Mark'], # noqa
                                                                    'grade': values[sub]['Grade'] if 'Grade' in values[sub] else None,  # noqa
                                                                    'final': values[sub]['Grade'] if 'Grade' in values[sub] else None  # noqa
                                                                })]
                                                        })
                                if type(value1) is str or type(value1) is float:
                                    pass
                                else:
                                    ac_year = self.env['op.academic.term'].search([
                                        ('name', '=', key1),
                                        ('academic_year_id', '=', res.id)])
                                    for sub in value1:
                                        for rec in subject:
                                            if key == res.name:
                                                if sub == rec.name:
                                                    self.write({
                                                        'grade_override': [(0, 0, {
                                                            'term': ac_year.id,
                                                            'subject': rec.id,
                                                            'calculated': value1[sub]['Mark'] if 'Mark' in value1[sub] else None, # noqa,
                                                            'grade': value1[sub]['Grade'] if 'Grade' in value1[sub] else None, # noqa
                                                            'final': value1[sub]['Grade'] if 'Grade' in value1[sub] else None # noqa
                                                        })]
                                                    })

    @api.onchange('grade_override')
    def calculate_override_grade(self):
        # for i in self.grade_override:
        subject = self.env['op.subject'].sudo().search([])
        students = self.env['gradebook.gradebook'].search([])
        quarter_average = []
        sem_average = []
        semester_average = []
        year_average = []
        acad_average = []
        # for student in students:
        if self.student_id:
            for res in self.gradebook_line_id:
                terms = json.loads(self.gradebook)
                for key, value in terms.items():
                    if type(value) is str or type(value) is float or\
                            type(value) is bool:
                        pass
                    else:
                        for key1, value1 in value.items():
                            if type(value1) is str or type(value1) is float:
                                pass
                            else:
                                for key2, value2 in value1.items():
                                    if type(value2) is float:
                                        pass
                                    else:
                                        for sub in value2 or []:
                                            for a in self.grade_override:
                                                for rec in subject:
                                                    if key2 == a.term.name:
                                                        if key == a.term.\
                                                                academic_year_id.name:
                                                            if sub == rec.name:
                                                                if sub == a.subject.\
                                                                        name:
                                                                    if a.override:
                                                                        if not res.course_id.grade_scale_id.op_grade_type_ids: # noqa
                                                                            value2[sub]['override'] = a.override # noqa
                                                                        else:
                                                                            for scale in res.course_id.grade_scale_id.op_grade_type_ids:  # noqa
                                                                                if (a.override >= scale.min_percentage) and (a.override <= scale.max_percentage):  # noqa
                                                                                    grade = scale.name # noqa
                                                                                    a.final = grade # noqa
                                                                                    value2[sub]['override'] = a.override # noqa
                                                                                    value2[sub]['Grade'] = a.final # noqa
                                                                        quarter_average.append(a.override)  # noqa
                                                                    else:
                                                                        quarter_average.append(float(value2[sub]['Mark']))  # noqa
                                                                        value2[sub]['override'] = value2[sub]['Mark'] # noqa

                                                                    if a.comment:
                                                                        value2[sub]['Comment'] = a.comment  # noqa
                                                if key == a.term.academic_year_id.name:
                                                    if key2 == a.subject.name:
                                                        if a.comment:
                                                            value2.update({
                                                                'Comment': a.comment})
                                                        if a.override:
                                                            if not res.course_id.\
                                                                    grade_scale_id.\
                                                                    op_grade_type_ids:
                                                                value1.update(
                                                                    {'override': a.
                                                                        override
                                                                     })
                                                            else:
                                                                for scale in res.course_id.grade_scale_id.op_grade_type_ids:  # noqa
                                                                    if (a.override >= scale.min_percentage) and (a.override <= scale.max_percentage):  # noqa
                                                                        grade = scale. \
                                                                            name
                                                                        a.final = \
                                                                            grade
                                                                        value2.update({'override': a.override}) # noqa
                                                                        value2['Grade'] = a.final # noqa
                                                            semester_average.\
                                                                append(a.override)
                                                        else:
                                                            semester_average.append(float(value2['Mark'])) # noqa
                                                            value2['override'] = value2['Mark'] # noqa

                                    if quarter_average:
                                        for a in self.grade_override:
                                            if key == a.term.academic_year_id.name:
                                                if key2 == a.term.name:
                                                    if not a.subject:
                                                        if a.comment:
                                                            value1[key2][
                                                                'Comment'] = a.comment
                                                        if a.override:
                                                            for scale in res. \
                                                                    course_id. \
                                                                    grade_scale_id. \
                                                                    op_grade_type_ids:
                                                                if (a.override >= scale.min_percentage) and (a.override <= scale.max_percentage):  # noqa
                                                                    grade = scale.name
                                                                    a.final = grade

                                                            value1[key2]['override'] = a.override # noqa

                                                            value1[key2]['Grade'] = a. \
                                                                final
                                                            sem_average.append(
                                                                a.override)
                                                        else:
                                                            average = (sum(
                                                                quarter_average) / len(
                                                                quarter_average))
                                                            sem_average.append(average)
                                                            value1[key2]['override'] = \
                                                                "{:0.2f}".format(
                                                                    average)

                                    quarter_average = []
                            if sem_average:
                                for a in self.grade_override:
                                    if key == a.term.academic_year_id.name:
                                        if key1 == a.term.name:
                                            if not a.subject:
                                                if a.comment:
                                                    value1['Comment'] = a.comment
                                                if a.override:
                                                    for scale in res.course_id. \
                                                            grade_scale_id. \
                                                            op_grade_type_ids:
                                                        if (a.override >= scale.min_percentage) and (a.override <= scale.max_percentage):  # noqa
                                                            grade = scale.name
                                                            a.final = grade
                                                            if scale.form_factor:
                                                                gpa = float(
                                                                    "{:0.2f}".format(
                                                                        a.override)
                                                                ) / scale.factor
                                                            else:
                                                                gpa = scale.gpa_value
                                                    value1['override'] = a.override
                                                    value1['Grade'] = a.final
                                                    value1['GPA'] = "{:0.2f}".\
                                                        format(gpa)
                                                    sem = float(value1['Total'])
                                                    year_average.append(a.override)
                                                else:
                                                    sem = (sum(sem_average) / len(
                                                        sem_average))
                                                    year_average.append(sem)
                                                    value1['override'] = "{:0.2f}". \
                                                        format(sem)

                                                    # value1['override'] = "{:0.2f}".\
                                                    #     format(sem)
                            elif semester_average:
                                for a in self.grade_override:
                                    if key == a.term.academic_year_id.name:
                                        if key1 == a.term.name:
                                            if not a.subject:
                                                if a.comment:
                                                    value1['Comment'] = a.comment
                                                if a.override:
                                                    for scale in res.course_id. \
                                                            grade_scale_id. \
                                                            op_grade_type_ids:
                                                        if (a.override >= scale.min_percentage) and (a.override <= scale.max_percentage):  # noqa
                                                            grade = scale.name
                                                            a.final = grade
                                                            if scale.form_factor:
                                                                gpa = float(
                                                                    "{:0.2f}".format(
                                                                        a.override)
                                                                ) / scale.factor
                                                            else:
                                                                gpa = scale.gpa_value
                                                    value1['override'] = a.override
                                                    value1['Grade'] = a.final
                                                    value1['GPA'] = "{:0.2f}".\
                                                        format(gpa)
                                                    sem = float(value1['Total'])
                                                    year_average.append(a.override)
                                                else:
                                                    sem = (sum(semester_average) / len(
                                                        semester_average))
                                                    year_average.append(sem)
                                                    value[key1][
                                                        'override'] = "{:0.2f}".\
                                                        format(sem)
                                            # semester_average = []
                            sem_average = []
                            semester_average = []

                    if year_average:
                        academic = "{:0.2f}".format(
                            sum(year_average) / len(year_average))
                        terms[key]['override'] = academic
                        acad_average.append(float(academic))
                    self.percentage = "{:0.2f}".format(
                        sum(acad_average) / len(acad_average))
                    students = self.env['op.student.progression'].search([])
                    self.gradebook = json.dumps(terms, indent=4)
                    for student in students:
                        if student.student_id == self.grade_override.\
                                grade_grade_id.student_id:
                            student.grade_book = json.dumps(terms, indent=4)
                    year_average = []
                break

    def recompute_data(self):
        for record in self.grade_override:
            record.unlink()
        self.calculation_main()
        self.student_Grade_override()

    def get_json_data_in_report(self, c_id):
        data = []
        total_credit = []
        subject_data = []
        subject_data_1 = []
        student = self.env['gradebook.gradebook'].search([('id', '=', int(c_id))])
        if student.gradebook:
            gradebook = json.loads(student.gradebook)
            for key, value in gradebook.items(): # noqa
                if type(value) != bool:
                    for key1, value1 in value.items():
                        q_index = 0
                        if type(value1) is dict:
                            for k, v in value1.items():
                                if type(v) is str or type(v) is float:
                                    pass
                                else:
                                    if gradebook["Quarter_term"]:
                                        for key2, value2 in v.items():
                                            if type(value2) is float or\
                                                    type(value2) is str:
                                                pass
                                            else:
                                                total_credit.append(
                                                    value2[
                                                        'Credit'
                                                    ] if 'Credit' in value2 else None)
                                                subject_data.append({
                                                    'subject_name': key2,
                                                    'subject_credit': value2['Credit'] if 'Credit' in value2 else None, # noqa
                                                    'subject_grade': value2['Grade'] if 'Grade' in value2 else None, # noqa
                                                    'subject_mark': value2['override'] if 'override' in value2 else value2['Mark'], # noqa
                                                    'subject_code': value2['Code'],
                                                })
                                        q = {
                                            k: subject_data,
                                            'semester_total': v['override'] if 'override' in v else v['Total'],  # noqa
                                            'total_credit': sum(total_credit)

                                        }

                                        if q_index == 1:
                                            q.update({
                                                'semester_gpa': value1[
                                                    'GPA'] if 'GPA' in value1 else None,
                                                'semester_name': key1,
                                            })
                                            q_index += 1
                                        if q_index == 0:
                                            q_index += 1

                                        data.append(q)
                                    else:
                                        total_credit.append(
                                            v['Credit'] if 'Credit' in v else None)
                                        subject_data_1.append({
                                            'subject_name': k,
                                            'subject_credit': v['Credit'] if 'Credit' in v else None, # noqa
                                            'subject_grade': v['Grade'] if 'Grade' in v else None, # noqa
                                            'subject_mark': v['override'] if v['override'] in v else v['Mark'], # noqa
                                            'subject_code': v['Code'],

                                        })

                                subject_data = []

                            if subject_data_1:
                                data.append({
                                    key1: subject_data_1,
                                    'semester_total': value1['override'] if 'override' in value1 else value1['Total'], # noqa
                                    'semester_gpa': value1['GPA'] if 'GPA' in value1 else None, # noqa
                                    'total_credit': sum(total_credit)
                                })
                            subject_data_1 = []
            return data

    def get_json_data_comment_report(self, c_id):
        data = []
        subject_data = []
        student = self.env['gradebook.gradebook'].search([('id', '=', int(c_id))])
        if student.gradebook:
            gradebook = json.loads(student.gradebook)
            for key, value in gradebook.items(): # noqa
                if type(value) != bool:
                    for key1, value1 in value.items():
                        if type(value1) is dict:
                            for k, v in value1.items():
                                if type(v) is str or type(v) is float:
                                    pass
                                else:
                                    if gradebook['Quarter_term']:
                                        for key2, value2 in v.items():
                                            if type(value2) is float or\
                                                    type(value2) is str:
                                                pass
                                            else:
                                                subject_data.append({
                                                    'subject_name': key2,
                                                    'subject_comment': value2['Comment'] if 'Comment' in value2 else None, # noqa
                                                })

                                        data.append({
                                            'semester': k,
                                            'subject_data': subject_data,
                                        })
                                    else:
                                        subject_data.append({
                                            'subject_name': k,
                                            'subject_comment': v['Comment'] if 'Comment' in v else None,  # noqa
                                        })
                                        data.append({
                                            'semester': key1,
                                            'subject_data': subject_data,
                                        })
                                    subject_data = []
            return data

    def get_academic_year(self):
        data = []
        if self.gradebook_line_id:
            for record in self.gradebook_line_id:
                data.append({
                    'year': record.academic_year_id.name,
                    'start_date': record.academic_year_id.start_date,
                    'end_date': record.academic_year_id.end_date,
                })
                break
            return data

    def update_student_override_data(self, data=None):
        if self.grade_override:
            domain = [('grade_grade_id', '=', self.id)]
            if 'Quarter' in data.keys():
                domain += [('term', '=', data['Quarter'])]
            else:
                domain += [('term', '=', data['Semester'])]
            if 'Subject' in data.keys():
                domain += [('subject', '=', data['Subject'])]
            else:
                domain += [('subject', '=', False)]
            temp = self.grade_override.search(domain)
            if data['Final Grades']:
                temp.update({
                    'override': float(data['Final Grades']),
                })
            self.calculate_override_grade()
            return True
        else:
            return False

    def _portal_ensure_token(self):
        if not self.access_token:
            self.sudo().write({'access_token': str(uuid.uuid4())})
        return self.access_token

    def _get_report_base_filename(self):
        self.ensure_one()
        return 'Grade Report'

    def get_unofficial_report_portal_url(self, suffix=None, report_type=None,
                                         download=None, query_string=None,
                                         anchor=None):
        self.ensure_one()
        url = self.report_access_url + '%s?access_token=%s%s%s%s%s' % (
            suffix if suffix else '',
            self._portal_ensure_token(),
            '&report_type=%s' % report_type if report_type else '',
            '&download=true' if download else '',
            query_string if query_string else '',
            '#%s' % anchor if anchor else ''
        )
        return url

    def action_view_student_statistics(self):
        action = self.env.ref("openeducat_grading.student_action_view").read()[0]
        action['params'] = {'gradebook_id': self.ids}
        action['context'] = {
            'active_id': self.id,
            'active_ids': self.ids,
            'search_default_name': self.student_id.name,
        }
        return action
