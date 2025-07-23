# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class OpAssignment(models.Model):
    _inherit = "op.assignment"

    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)

    attachment_ids = fields.One2many('ir.attachment', 'res_id',
                                     domain=[('res_model', '=',
                                              'op.assignment')],
                                     string='Attachments',
                                     readonly=True)
    attempt_type = fields.Selection([
        ('single', 'Single Attempt'),
        ('multiple', 'Multiple Attempt')],
        'Number of Attempt', default='single', required=True)
    max_attempt = fields.Integer("Max Attempt")
    additional_attempt = fields.One2many(
        'student.additional.attempt',
        'assignment_id', string='Student Additonal Attempt')

    @api.onchange('attempt_type')
    def get_attempt(self):
        if self.attempt_type == 'single':
            self.max_attempt = 1
        else:
            self.max_attempt = 0

    def unlink(self):
        for record in self:
            if not record.state == 'draft' and not self.env.user.has_group(
                    'openeducat_assignment.group_op_assignment_user'):
                raise ValidationError(
                    _("You can't delete none draft submissions!"))
        res = super(OpAssignment, self).unlink()
        return res

    def write(self, vals):
        if self.env.user.child_ids:
            raise Warning(_('Invalid Action!\n Parent can not edit \
               Assignment Submissions!'))
        return super(OpAssignment, self).write(vals)

    def search_read_for_app(self, offset=0, limit=None, order=None):
        if self.env.user.partner_id.is_student:
            partner = self.env.user.partner_id
            domain = ([('state', '=', 'publish'),
                       ('allocation_ids.partner_id', '=', partner.id)])
            evaluation_field = self.env['ir.module.module'].sudo().search(
                [('name', '=', 'openeducat_assignment_grading_enterprise')])
            if evaluation_field.state == 'installed':
                fields = ['name', 'batch_id', 'course_id', 'subject_id',
                          'assignment_type_id', 'faculty_id', 'issued_date',
                          'submission_date', 'marks', 'allocation_ids',
                          'description', 'state', 'evaluation_type']
            else:
                fields = ['name', 'batch_id', 'course_id', 'subject_id',
                          'assignment_type_id', 'faculty_id', 'issued_date',
                          'submission_date', 'marks', 'allocation_ids',
                          'description', 'state', ]
            res = self.sudo().search_read(domain=domain, fields=fields,
                                          offset=offset, limit=limit, order=order)
            return res

        elif self.env.user.partner_id.is_parent:
            user = self.env.user
            parent_id = self.env['op.parent'].sudo().search(
                [('user_id', '=', user.id)])

            student_id = [student.id for student in parent_id.student_ids]
            domain = [('allocation_ids', 'in', student_id)]
            evaluation_field = self.env['ir.module.module'].sudo().search(
                [('name', '=', 'openeducat_assignment_grading_enterprise')])
            if evaluation_field.state == 'installed':
                fields = ['name', 'batch_id', 'course_id', 'subject_id',
                          'assignment_type_id', 'faculty_id', 'issued_date',
                          'submission_date', 'marks', 'allocation_ids',
                          'description', 'state', 'evaluation_type']
            else:
                fields = ['name', 'batch_id', 'course_id', 'subject_id',
                          'assignment_type_id', 'faculty_id', 'issued_date',
                          'submission_date', 'marks', 'allocation_ids',
                          'description', 'state', ]
            res = self.sudo().search_read(domain=domain, fields=fields,
                                          offset=offset, limit=limit, order=order)
            return res

        elif self.user_has_groups('openeducat_assignment.group_op_assignment_user'):
            user = self.env.user
            faculty_id = self.env['op.faculty'].sudo().search(
                [('user_id', '=', user.id)])
            domain = [('faculty_id', '=', faculty_id.id)]

            evaluation_field = self.env['ir.module.module'].sudo().search(
                [('name', '=', 'openeducat_assignment_grading_enterprise')])
            if evaluation_field.state == 'installed':
                fields = ['name', 'batch_id', 'course_id', 'subject_id',
                          'assignment_type_id', 'faculty_id', 'issued_date',
                          'submission_date', 'marks', 'allocation_ids',
                          'description', 'state', 'evaluation_type']
            else:
                fields = ['name', 'batch_id', 'course_id', 'subject_id',
                          'assignment_type_id', 'faculty_id', 'issued_date',
                          'submission_date', 'marks', 'allocation_ids',
                          'description', 'state', ]
            res = self.sudo().search_read(domain=domain, fields=fields,
                                          offset=offset, limit=limit, order=order)
            return res

    def search_read_for_assignment_allocation(self):
        active_students = self.env['op.student.course'].sudo().search_read(
            domain=[('student_id.active', '=', True)],
            fields=['batch_id', 'course_id', 'student_id'])
        return active_students


class StudentAdditonalAttempt(models.Model):
    _name = "student.additional.attempt"
    _description = "Multiple Submission Attempt"

    assignment_id = fields.Many2one('op.assignment', string='Assignment')
    student_id = fields.Many2one('op.student', string='Student')
    datetime = fields.Datetime('Date', default=lambda self: fields.Datetime.now())
    allowed_attempt = fields.Integer(string='Allowed Additional Attempt(s)')
    create_by = fields.Many2one('res.users', 'Created By',
                                default=lambda self: self._uid, readonly=True)
