# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

import datetime

from odoo import _, api, fields, models


class Grievance(models.Model):
    _name = "grievance"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'website.published.mixin']
    _description = "Grievance"

    def get_emails(self):
        email_ids = ''
        for team in self.grievance_team_id:
            for leader in team.team_leader:
                if email_ids:
                    email_ids = email_ids + ',' + str(leader.sudo().partner_id.email)
                else:
                    email_ids = str(leader.sudo().partner_id.email)
            for member in team.member_ids:
                if email_ids:
                    email_ids = email_ids + ',' + str(member.sudo().partner_id.email)
                else:
                    email_ids = str(member.sudo().partner_id.email)
        return email_ids

    def _composer_format(self, res_model, res_id, template):
        compose_form = self.env.ref(
            'mail.email_compose_message_wizard_form', False)
        ctx = dict(
            default_model=res_model,
            default_res_id=res_id,
            default_use_template=bool(template),
            default_template_id=template and template.id or False,
            default_composition_mode='comment',
            force_email=True,
        )
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }

    def send_mail(self):
        template = self.env.ref(
            'openeducat_grievance_enterprise.mail_template_gms',
            raise_if_not_found=False)
        return self._composer_format(res_model='grievance',
                                     res_id=self.id,
                                     template=template)

    def send_mail_for_resolution(self):
        template = self.env.ref(
            'openeducat_grievance_enterprise.mail_template_gms_for_resolution',
            raise_if_not_found=False)
        return self._composer_format(res_model='grievance',
                                     res_id=self.id,
                                     template=template)

    def inreview_progressbar(self):
        self.write({
            'state': 'in_review',
        })
        template = self.env.ref(
            'openeducat_grievance_enterprise.mail_template_gms_assign',
            raise_if_not_found=False)
        # res_id = self.id
        # template.send_mail(res_id=res_id, force_send=True)

        return self._composer_format(res_model='grievance',
                                     res_id=self.id,
                                     template=template)

    def submitted_progressbar(self):
        self.write({
            'state': 'submitted',
            'created_date': datetime.date.today()
        })

    def close_progressbar(self):
        self.write({
            'state': 'close',
        })

    def resolve_progressbar(self):
        self.write({
            'state': 'resolve',
        })
        template = self.env.ref(
            'openeducat_grievance_enterprise.mail_template_gms_for_resolution',
            raise_if_not_found=False)
        # res_id = self.id
        # template.send_mail(res_id=res_id, force_send=True)
        return self._composer_format(res_model='grievance',
                                     res_id=self.id,
                                     template=template)

    def reject_progressbar(self):
        self.write({
            'state': 'reject',
        })

        template = self.env.ref(
            'openeducat_grievance_enterprise.mail_template_gms_rejection',
            raise_if_not_found=False)
        # res_id = self.id
        # template.send_mail(res_id=res_id, force_send=True)
        return self._composer_format(res_model='grievance',
                                     res_id=self.id,
                                     template=template)

    def cancel_progressbar(self):
        self.write({
            'state': 'cancel',
        })

    @api.onchange('grievance_category_id')
    def onchange_grievance_category_id(self):
        team_records = self.env['grievance.team'].search([])
        if self.grievance_category_id:
            for data in team_records: # noqa
                record = self.env['grievance.team'].search(
                    [('grievance_category_id', '=', self.grievance_category_id.id)])
                for rec in record:
                    if record:
                        self.grievance_team_id = rec.id
                    else:
                        self.grievance_team_id = False

            if self.is_academic is False:
                self.course_id = False
                self.batch_id = False
                self.academic_year_id = False
                self.academic_term_id = False

    @api.onchange('course_id')
    def onchange_course_id(self):
        if self.course_id:
            batch_ids = self.env['op.batch'].search([
                ('course_id', '=', self.course_id.id)])
            return {'domain': {'batch_id': [('id', 'in', batch_ids.ids)]}}

    @api.onchange('parent_id')
    def onchange_parent_id(self):
        parent_data = self.env['op.parent'].search([])
        student_list = []
        for data in parent_data:
            for student in data.student_ids:
                student_list.append(student.id)
        if self.parent_id:
            student_ids = self.env['op.student'].search([
                ('id', 'in', student_list)])
            return {'domain': {'student_id': [('id', 'in', student_ids.ids)]}}

    @api.onchange('academic_year_id')
    def onchange_academic_term_id(self):
        if self.academic_year_id:
            academic_year_ids = self.env['op.academic.year']. \
                browse(self.academic_year_id.id)
            return {'domain': {'academic_term_id': [
                ('id', 'in', academic_year_ids.ids)]}}

    @api.onchange("grievance_for")
    def student_or_faculty(self):
        if self.grievance_for == 'student':
            self.faculty_id = None
            self.parent_id = None

        if self.grievance_for == 'faculty':
            self.student_id = None
            self.parent_id = None

    name = fields.Char()
    subject = fields.Char("Name/Subject", required=True)
    created_date = fields.Date("Created Date",
                               default=datetime.date.today())
    description = fields.Text("Description", required=True)
    course_id = fields.Many2one("op.course", "Course")
    batch_id = fields.Many2one("op.batch", "Batch")
    academic_year_id = fields.Many2one("op.academic.year", "Academic Year")
    academic_term_id = fields.Many2one("op.academic.term", "Academic Term")
    grievance_category_id = fields.Many2one('grievance.category', "Grievance Category",
                                            required=True,
                                            domain=[('parent_id', '!=', False)])
    grievance_team_id = fields.Many2one('grievance.team', "Team",
                                        required=True, index=True, tracking=True)
    student_id = fields.Many2one('op.student', string="Student")
    faculty_id = fields.Many2one('op.faculty', string="Faculty")
    parent_id = fields.Many2one('op.parent', string="Parent")
    state = fields.Selection(
        [('draft', 'Draft'), ('submitted', 'Submitted'), ('in_review', 'In Review'),
         ('action', 'Action'), ('reject', 'Reject'), ('cancel', 'Cancel'),
         ('resolve', 'Resolve'), ('close', 'Close')], default="draft"
        , index=True, tracking=True)
    grievance_for = fields.Selection([('student', 'Student'),
                                     ('faculty', 'Faculty'), ('parent', 'Parent')],
                                     string="Grievance By",
                                     default="student",
                                     required=True)
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)
    is_academic = fields.Boolean(related='grievance_category_id.is_academic')
    attachment_ids = fields.One2many('ir.attachment', 'res_id',
                                     domain=[('res_model', '=', _name)],
                                     string="Attachments", required=True)
    root_cause_id = fields.Many2one('grievance.root.cause', 'Root Cause')
    action_taken = fields.Text("Action Taken")
    grievance_parent_id = fields.Many2one('grievance', 'Parent Grievance')
    is_satisfied = fields.Selection([('yes', 'Yes'), ('no', 'No')])
    is_appeal = fields.Boolean()
    color = fields.Integer('Color Index', default=1)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name'):
                seq = self.env['ir.sequence'].next_by_code('grievance.sequence')
                vals.update({'name': seq})
        result = super(Grievance, self).create(vals_list)
        for grievance in result:
            if grievance.grievance_team_id:
                member_list = []
                team_records = self.env['grievance.team']. \
                    browse(grievance.grievance_team_id.id)
                member_list.append(team_records.team_leader.partner_id.id)
                for member in team_records.member_ids:
                    if member.partner_id.id not in member_list:
                        member_list.append(member.partner_id.id)
                grievance.message_subscribe(partner_ids=member_list)

        return result
