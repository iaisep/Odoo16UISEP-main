# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from datetime import datetime

from odoo import _, api, fields, models


class OpStudentSkillAssessment(models.Model):
    _name = "op.student.skill.assessment"
    _description = "Student Skill Assessment"
    _inherit = ["mail.thread"]

    name = fields.Char(string='Name', required=True, copy=False, readonly=True,
                       index=True, default=lambda self: _('New'))
    student_skill_type_id = fields.Many2one('op.student.skill.type',
                                            'Skill Assessment Type', required=True)
    date = fields.Date(default=datetime.today())
    student_id = fields.Many2one('op.student', required=True)
    user_id = fields.Many2one(
        'res.users', 'Assessed By', default=lambda self: self.env.user.id)
    student_skill_assessment_line = fields.One2many(
        'op.student.skill.assessment.line', 'student_skill_assessment_id', 'Skills')
    state = fields.Selection(
        [('draft', 'Draft'), ('schedule', 'Scheduled'),
         ('cancel', 'Cancelled'), ('done', 'Done')], 'State', default='draft',
        tracking=True)

    @api.onchange('student_skill_type_id')
    def get_skills(self):
        if self.student_skill_type_id:
            if self.student_skill_assessment_line:
                for skill_id in self.student_skill_assessment_line:
                    skill_id.unlink()
            temp_list = []
            skill_type = self.env['op.student.skill.type'].sudo().search(
                [('id', '=', self.student_skill_type_id.id)])
            for skill in skill_type.student_skills_line:
                line_values = {
                    'student_skill_id': skill.id,
                    'student_skill_type_id': skill_type.id
                }
                temp_list.append(line_values)
            for skill_values in temp_list:
                self.write({
                    'student_skill_assessment_line': [(0, 0, skill_values)]
                })

    @api.model_create_multi
    def create(self, vals_list):
        result = super(OpStudentSkillAssessment, self).create(vals_list)
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                name = self.env['ir.sequence'].next_by_code(
                    'op.student.skill.assessment') or _('New')
                result.write({
                    'name': name
                })
        return result

    def act_draft(self):
        self.state = 'draft'

    def act_schedule(self):
        self.state = 'schedule'

    def act_done(self):
        self.state = 'done'
        student = self.env['op.student'].search([('id', '=', self.student_id.id)])
        temp_list = self.env['op.student.skill']
        c_temp_list = self.env['op.student.skill']
        write = self.env['op.student.skill']
        for line in student.student_skill_line:
            temp_list += line.student_skills_id
        for c_line in self.student_skill_assessment_line:
            c_temp_list += c_line.student_skill_id
        if len(c_temp_list) > len(temp_list):
            for list_id in c_temp_list:
                if list_id in temp_list:
                    continue
                else:
                    write += list_id
        elif len(c_temp_list) == len(temp_list):
            for list_id in c_temp_list:
                if list_id in temp_list:
                    continue
                else:
                    write += list_id
        else:
            for list_id in c_temp_list:
                if list_id in temp_list:
                    continue
                else:
                    write += list_id
        if temp_list:
            t_list = []
            for line in self.student_skill_assessment_line:
                if line.student_skill_id in temp_list:
                    temp_dict = {
                        'student_skill_type_id': self.student_skill_type_id.id,
                        'student_skills_id': line.student_skill_id.id,
                        'student_skill_level_id': line.student_skill_level_id.id
                    }
                    t_list.append(temp_dict)
            for line in student.student_skill_line:
                for data in t_list:
                    if data['student_skills_id'] == line.student_skills_id.id:
                        line.update(data)
        if write:
            w_list = []
            for line in self.student_skill_assessment_line:
                if line.student_skill_id in write:
                    temp_dict = {
                        'student_skill_type_id': self.student_skill_type_id.id,
                        'student_skills_id': line.student_skill_id.id,
                        'student_skill_level_id': line.student_skill_level_id.id
                    }
                    w_list.append(temp_dict)
            for data in w_list:
                student.write({
                    'student_skill_line': [(0, 0, data)]
                })

    def act_cancel(self):
        self.state = 'cancel'
