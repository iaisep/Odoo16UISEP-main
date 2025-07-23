# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import _, api, fields, models


class GradingAssigment(models.Model):
    _name = 'grading.assignment'
    _inherit = ['grading.assignment', 'mail.thread', 'mail.activity.mixin']

    _description = "Grading Assigment"

    sequence = fields.Char(string='Index', required=True,
                           copy=False, readonly=True,
                           index=True, default=lambda self: _('New'))
    name = fields.Char('Name', required=True)
    issued_date = fields.Datetime('Issued Date', required=True)
    course_id = fields.Many2one('op.course', 'Course', required=True)
    subject_id = fields.Many2one('op.subject', string='Subject')
    grade = fields.Many2one('op.grade.table', string='Grade')
    point = fields.Float('Points',
                         default=lambda self: self.grade.grade_table_ids is False)
    hide = fields.Boolean(compute='_compute_hide')
    hide_subject = fields.Boolean(compute='_compute_assignment_types')
    gradebook_line_id = fields.One2many('gradebook.line', 'grade_assigment_id',
                                        string='Gradebook Line')
    year_id = fields.Many2one('op.academic.year', string='Academic Year',
                              tracking=True)
    term_id = fields.Many2one('op.academic.term', string='Term',
                              tracking=True)
    active = fields.Boolean(default=True)
    user_id = fields.Many2one("res.users", string="User", required=True,
                              default=lambda self: self.env.user)

    state = fields.Selection(
        selection=[
            ('draft', 'Draft'), ('published', 'Published'),
            ('closed_for_submission', 'Closed For Submission'),
            ('grading_started', 'Grading Started'),
            ('grading_closed', 'Grading Closed'),
            ('grades_published', 'Grades Published'),
            ('cancelled', 'Cancelled')
        ], default='draft'
    )

    @api.model_create_multi
    def create(self, vals_list):
        res = super(GradingAssigment, self).create(vals_list)
        for vals in vals_list:
            if vals.get('sequence', '/') == '/':
                res.sequence = self.env['ir.sequence']. \
                    next_by_code('grading.assignment') or '/'
        return res

    @api.onchange('year_id')
    def terms_by_year(self):
        if self.year_id:
            lists = []
            year_ids = self.env['op.academic.year'].search([('id', '=',
                                                             self.year_id.id)])
            for i in year_ids.academic_term_ids:
                lists.append(i.id)
            domain = {'term_id': [('id', 'in', lists)]}
            result = {'domain': domain}
            return result

    @api.depends('grade')
    def _compute_hide(self):
        if self.grade.grade_table_ids:
            self.hide = True
        else:
            self.hide = False

    @api.onchange('assignment_type')
    def _compute_assignment_types(self):
        for record in self.assignment_type:
            if record.assign_type == 'attendance':
                self.hide_subject = True
            else:
                self.hide_subject = False

    def create_gradeline(self):
        grade_book = self.env['gradebook.gradebook'].search([
            ('academic_year_id.id', '=', self.year_id.id),
            ('course_id', '=', self.course_id.id)])
        course_detail = self.env['op.student.course'].search([
            ('course_id', '=', self.course_id.id)])
        create_line = self.env['gradebook.line'].search([
            ('grade_assigment_id', '=', self.id)])
        student_list = [student.gradebook_id.student_id.id for student in create_line]
        for name in grade_book:
            if course_detail.subject_ids:
                course_detail = course_detail.search([
                    ('subject_ids', 'in', self.subject_id.id)])
            for data in course_detail:
                if data.student_id.id == name.student_id.id and name.\
                        student_id.id not in student_list:
                    name.gradebook_line_id.create({
                        'gradebook_id': name.id,
                        'academic_year_id': self.year_id.id,
                        'academic_term_id': self.term_id.id,
                        'course_id': self.course_id.id,
                        'subject_id': self.subject_id.id,
                        'assignment_type_id': self.assignment_type.id,
                        'grade_assigment_id': self.id,
                        'grade_table_id': self.grade.id,
                    })
        return {
            'name': 'GradeBook Line',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'gradebook.line',
            'domain': [('grade_assigment_id.id', '=', self.id)]
        }

    def action_draft(self):
        for obj in self:
            obj.state = 'draft'
        return True

    def action_published(self):
        for obj in self:
            obj.state = 'published'
        return True

    def action_closed_for_submission(self):
        for obj in self:
            obj.state = 'closed_for_submission'
        return True

    def action_grading_started(self):
        for obj in self:
            obj.state = 'grading_started'
        return True

    def action_grading_closed(self):
        for obj in self:
            obj.state = 'grading_closed'
        return True

    def action_grades_published(self):
        for obj in self:
            obj.state = 'grades_published'
            for record in self.gradebook_line_id:
                for res in record.gradebook_id:
                    res.calculate_percentage()
                    res.calculate_attendance()
        return True

    def action_cancelled(self):
        for obj in self:
            obj.state = 'cancelled'
        return True

    def action_view_student_grade(self):
        action = self.env.ref('openeducat_grading.act_gradebook_line_view').read()[0]
        action['context'] = {
            'course_id': self.id
        }
        action['domain'] = [('grade_assigment_id', "=", self.id)]

        value = {
            'name': 'GradeBook Line',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'gradebook.line',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'current',
            'context': {'default_grade_assigment_id': self.id},
            'domain': [('grade_assigment_id', "=", self.id)]
        }
        return value

    def action_view_statistics(self):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "openeducat_grading.assignment_action_view")
        # action['params'] = {'assignment_id': self.ids}
        action['context'] = {
            'active_id': self.id,
            'active_ids': self.ids,
            'search_default_name': self.name,
        }
        return action


class OpAssignment(models.Model):
    _inherit = 'op.assignment'

    @api.onchange('year_id')
    def terms_by_year(self):
        if self.year_id:
            lists = []
            year_ids = self.env['op.academic.year'].search([
                ('id', '=', self.year_id.id)])
            for i in year_ids.academic_term_ids:
                lists.append(i.id)
            domain = {'term_id': [('id', 'in', lists)]}
            result = {'domain': domain}
            return result

    @api.model_create_multi
    def create(self, vals):
        for values in vals:
            if values.get('sequence', '/') == '/':
                values['sequence'] = self.env['ir.sequence']. \
                    next_by_code('grading.assignment') or '/'
        return super(OpAssignment, self).create(vals)
