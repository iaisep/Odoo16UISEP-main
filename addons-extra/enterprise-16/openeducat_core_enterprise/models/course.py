# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import fields, models


class OpCourse(models.Model):
    _inherit = "op.course"

    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)
    color = fields.Integer(string='Color Index', default=0)
    student_count = fields.Integer(
        compute="_compute_course_dashboard_data", string='Student Count')
    batch_count = fields.Integer(
        compute="_compute_course_dashboard_data", string='Batch Count')
    subject_count = fields.Integer(
        compute="_compute_course_dashboard_data", string='Subject Count')

    child_course_count = fields.Integer(
        compute="_compute_child_course_count_dashboard_data")

    faculty_count = fields.Integer(
        compute="_compute_count_faculty",
        string='Faculty Count')

    def _compute_child_course_count_dashboard_data(self):
        for course in self:
            child_course_list = self.env['op.course'].search_count(
                [('parent_id', 'in', [course.id])])
            course.child_course_count = child_course_list

    def _compute_course_dashboard_data(self):
        for course in self:
            student_list = self.env['op.student'].search_count(
                [('course_detail_ids.course_id', 'in', [course.id])])
            batch_list = self.env['op.batch'].search_count(
                [('course_id', 'in', [course.id])])
            subject_list = self.env['op.subject'].search_count(
                [('course_id', 'in', [course.id])])

            course.student_count = student_list
            course.subject_count = subject_list
            course.batch_count = batch_list

    def action_onboarding_course_layout(self):
        self.env.user.company_id.onboarding_course_layout_state = 'done'

    subject_counts = fields.Integer(compute='_compute_count_subject')

    def get_subject(self):
        for record in self:
            for subjects in record.subject_ids: # noqa
                action = self.env.ref(
                    'openeducat_core_enterprise.'
                    'act_dashboard_op_subject_view').read()[0]
                return action

    def _compute_count_subject(self):
        for record in self:
            subjects = len(record.subject_ids)
            record.subject_counts += subjects

    def get_faculty(self):
        faculty_ids = self.env['op.faculty'].search([
            ('faculty_subject_ids', 'in', self.subject_ids.ids)])
        action = self.env.ref(
            'openeducat_core.act_open_op_faculty_view').read()[0]
        action['domain'] = [('id', 'in', faculty_ids.ids)]
        return action

    def _compute_count_faculty(self):
        for record in self:
            faculty = self.env['op.faculty'].search_count([
                ('faculty_subject_ids', 'in', record.subject_ids.ids)])
            record.faculty_count = faculty
