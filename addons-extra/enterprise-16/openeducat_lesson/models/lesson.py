# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class OpLesson(models.Model):
    _name = "op.lesson"
    _inherit = ['mail.thread']
    _description = "Lesson"

    def _default_faculty(self):
        return self.env['op.faculty'].search([
            ('user_id', '=', self._uid)
        ], limit=1) or False

    name = fields.Char(string="Lecture Name",
                       default=lambda self: self.env['ir.sequence']
                       .next_by_code('op.lesson') or '/', required=True)
    course_id = fields.Many2one('op.course', string='Course', required=True)
    batch_id = fields.Many2one('op.batch', string='Batch', required=True)
    subject_id = fields.Many2one('op.subject', string='Subject', required=True)
    lesson_topic = fields.Text(string="Lecture Topic", required=True)
    faculty_id = fields.Many2one('op.faculty', string='Faculty',
                                 default=lambda self: self._default_faculty())
    start_datetime = fields.Datetime(
        string='Start Time',
        default=lambda self: fields.Datetime.now())
    end_datetime = fields.Datetime(string='End Time')
    session_ids = fields.Many2many("op.session", "lesson_session_rel_1",
                                   string="Session")
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)
    active = fields.Boolean(default=True)
    state = fields.Selection(
        [('draft', 'Draft'), ('plan', 'Planned'),
         ('conduct', 'Conducted'), ('cancel', 'Cancelled')],
        'Status', default='draft', tracking=True)

    def lesson_draft(self):
        self.state = 'draft'

    def lesson_plan(self):
        self.state = 'plan'

    def lesson_conduct(self):
        self.state = 'conduct'

    def lesson_cancel(self):
        self.state = 'cancel'

    @api.constrains('start_datetime', 'end_datetime')
    def _check_date_time(self):
        if self.start_datetime > self.end_datetime:
            raise ValidationError(_(
                'End Time cannot be set before Start Time.'))

    @api.onchange('course_id')
    def onchange_course_id(self):
        if self.course_id:
            batch_ids = self.env['op.batch'].search([
                ('course_id', '=', self.course_id.id)])
            return {'domain': {'batch_id': [('id', 'in', batch_ids.ids)]}}

    @api.onchange('course_id')
    def onchange_course(self):
        if self.course_id:
            subject_id = self.env['op.course'].search([
                ('id', '=', self.course_id.id)]).subject_ids
            return {
                'domain': {'subject_id': [('id', 'in', subject_id.ids)]}}

    @api.onchange('faculty_id')
    def onchange_faculty_id(self):
        if self.faculty_id:
            session_ids = self.env['op.faculty'].search([
                ('id', '=', self.faculty_id.id)]).session_ids
            return {
                'domain': {'session_ids': [('id', 'in', session_ids.ids)]}
            }


class OpSession(models.Model):
    _inherit = 'op.session'

    lesson_ids = fields.Many2many("op.lesson", "lesson_session_rel_1",
                                  string="Lesson", readonly=True)
