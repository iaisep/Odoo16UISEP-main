# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

import json

from odoo import _, api, fields, models


class OpHonorRoll(models.Model):
    _name = 'op.honorroll'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    _description = "Honor Roll"
    name = fields.Char(string='Name', required=True, copy=False, readonly=True,
                       index=True, default=lambda self: _('New'))
    year_id = fields.Many2one('op.academic.year', string='Academic Year',
                              required=True)
    course_id = fields.Many2one('op.course', 'Course', required=True)
    subject_id = fields.Many2one('op.subject', string='Subject')
    honor_line_id = fields.One2many('op.honorroll.line', 'honor_id',
                                    string='Honor Line')
    from_per = fields.Float(string='From Percentage', required=True)
    to_per = fields.Float(string='To Percentage', required=True)
    description = fields.Text(string="Description", required=True)
    background = fields.Image('Background Image', attachment=True)
    active = fields.Boolean(default=True)

    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)

    state = fields.Selection(
        selection=[
            ('draft', 'Draft'), ('generate', 'Generated'),
            ('cancel', 'Cancel')
        ], default='draft'
    )

    @api.model_create_multi
    def create(self, vals_list):
        res = super(OpHonorRoll, self).create(vals_list)
        for vals in vals_list:
            if vals.get('sequence', '/') == '/':
                res.name = self.env['ir.sequence']. \
                    next_by_code('op.honorroll') or '/'
        return res

    def generate_honor_roll(self):
        students = self.env['gradebook.gradebook'].search([
            ('academic_year_id.id', '=', self.year_id.id)])
        honor = self.env['op.honorroll.line'].search([])
        self.honor_line_id = None
        for student in students:
            for course in self.course_id:
                course_id = self.env['op.student.course'].search(
                    [('course_id', '=', course.id)])
                for data in course_id:
                    if data.student_id.id == student.student_id.id:
                        result = student.gradebook
                        terms = json.loads(result)
                        for key, value in terms.items():
                            if key == self.year_id.name:
                                if self.subject_id:
                                    for key1, value1 in value.items(): # noqa
                                        if type(value1) is str or type(value1) is float:
                                            pass
                                        else:
                                            for k1, v1 in value1.items():
                                                if k1.startswith('Quarter'):
                                                    for sub in v1 or []:
                                                        if sub == self.subject_id.name:
                                                            if self.from_per <= float(
                                                                    v1['Total']
                                                            ) <= self.to_per:
                                                                honor.create({
                                                                    'student_id':
                                                                        student.
                                                                        student_id.id,
                                                                    'year_id': self.
                                                                    year_id.id,
                                                                    'course_id': self.
                                                                    course_id.id,
                                                                    'subject_id': self.
                                                                    subject_id.id,
                                                                    'percentage': v1[
                                                                        'Total'],
                                                                    'honor_id': self.id
                                                                })
                                        if type(value1) is str or type(value1) is float:
                                            pass
                                        else:
                                            for sub in value1 or []:
                                                if sub == self.subject_id.name:
                                                    if self.from_per <= float(
                                                            value1[sub]['Mark']
                                                    ) <= self.to_per:
                                                        honor.create({
                                                            'student_id': student.
                                                            student_id.id,
                                                            'year_id': self.year_id.id,
                                                            'course_id': self.
                                                            course_id.id,
                                                            'subject_id': self.
                                                            subject_id.id,
                                                            'percentage': value1[sub][
                                                                'Mark'],
                                                            'honor_id': self.id
                                                        })
                                else:
                                    if self.from_per <= float(
                                            value['Year Total']) <= self.to_per:
                                        honor.create({
                                            'student_id': student.student_id.id,
                                            'year_id': self.year_id.id,
                                            'course_id': self.course_id.id,
                                            'percentage': value['Year Total'],
                                            'honor_id': self.id
                                        })
                                for obj in self:
                                    obj.state = 'generate'

    def action_draft(self):
        for obj in self:
            obj.state = 'draft'
        return True

    def action_generate(self):
        for obj in self:
            obj.state = 'generate'
        return True

    def action_cancel(self):
        for obj in self:
            obj.state = 'cancel'
        return True
