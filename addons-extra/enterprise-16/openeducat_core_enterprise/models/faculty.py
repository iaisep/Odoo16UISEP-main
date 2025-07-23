# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from datetime import date, datetime

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class OpFaculty(models.Model):
    _inherit = "op.faculty"

    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)
    subject_count = fields.Integer(compute='_compute_count_subjects')

    def get_subjects(self):
        for record in self:
            action = self.env.ref(
                'openeducat_core.act_open_op_subject_view').read()[0]
            action['domain'] = [('id', 'in', record.faculty_subject_ids.ids)]
        return action

    def _compute_count_subjects(self):
        for record in self:
            subjects = len(record.faculty_subject_ids)
            record.subject_count += subjects

    @api.model
    def get_dashboard_data(self):
        user = self.env['res.users'].browse(self._uid)
        faculty = self.env['op.faculty'].search(
            [('partner_id', '=', user.partner_id.id)])
        data = {'faculty_id': faculty.id, 'change_req': 0, 'submitted': 0,
                'accepted': 0, 'today': 0, 'this_week': 0}
        assignment = self.env['ir.model'].search(
            [('model', '=', 'op.assignment.sub.line')])
        if assignment and faculty:
            op_assignment_sub_line = self.env['op.assignment.sub.line']
            change = op_assignment_sub_line.search_count([
                ('faculty_id', '=', faculty.id), ('state', '=', 'change')])
            submit = op_assignment_sub_line.search_count([
                ('faculty_id', '=', faculty.id), ('state', '=', 'submit')])
            accept = op_assignment_sub_line.search_count([
                ('faculty_id', '=', faculty.id), ('state', '=', 'accept')])
            data['change_req'] = change
            data['submitted'] = submit
            data['accepted'] = accept
        timetable = self.env['ir.model'].search(
            [('model', '=', 'op.timetable')])
        if timetable and faculty:
            first_day = (datetime.today() -
                         relativedelta(days=date.today().weekday())) \
                .strftime('%Y-%m-%d 00:00:00')
            last_day = (datetime.today() +
                        relativedelta(days=6 - date.today().weekday())) \
                .strftime('%Y-%m-%d 23:59:59')
            today = self.env['op.timetable'].search_count([
                ('faculty_id', '=', faculty.id),
                ('start_datetime', '>=',
                 datetime.today().strftime('%Y-%m-%d 00:00:00')),
                ('start_datetime', '<=',
                 datetime.today().strftime('%Y-%m-%d 23:59:59'))])
            this_week = self.env['op.timetable'].search_count([
                ('faculty_id', '=', faculty.id),
                ('start_datetime', '>=', first_day),
                ('start_datetime', '<=', last_day)])
            data['today'] = today
            data['this_week'] = this_week
        return data

    @api.depends('faculty_subject_ids.course_id')
    def get_courses(self):
        for record in self:
            action = self.env.ref(
                'openeducat_core.act_open_op_course_view').read()[0]
            action['domain'] = \
                [('id', '=', record.faculty_subject_ids.course_id.ids)]
            return action
