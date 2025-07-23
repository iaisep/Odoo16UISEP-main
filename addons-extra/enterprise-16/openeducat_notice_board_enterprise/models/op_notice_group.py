# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

import datetime

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class OpNoticeGroup(models.Model):
    _name = "op.notice.group"
    _description = "Groups"

    name = fields.Char(string="Name", required=True)

    course_ids = fields.Many2many("op.course", "course_notice_group_id",
                                  string="Courses")
    batch_ids = fields.Many2many("op.batch", "batch_notice_group_id",
                                 string="Batches",
                                 domain="[('course_id' , 'in' , course_ids)]")
    student_visibility = fields.Selection([('all_students', 'By Course & Batch'),
                                           ('selected_students', 'Selected Students')])
    student_ids = fields.Many2many("op.student", string="Students",
                                   default=False, store=True,
                                   compute="_compute_target_student_audience")
    parent_course_ids = fields.Many2many("op.course", "parent_course_notice_group_id")
    parent_batch_ids = fields.Many2many("op.batch", "parent_batch_notice_group_id",
                                        domain="[('course_id', 'in',"
                                               "parent_course_ids)]")
    parent_visibility = fields.Selection([('all_parents', 'By Course & Batch'),
                                          ('selected_parents', 'Selected Parents')])
    parent_ids = fields.Many2many("op.parent", string="Parents", store=True,
                                  compute="_compute_target_parent_audience")
    faculty_visibility = fields.Selection([('all_faculty', 'All Faculties'),
                                           ('selected_faculty', 'Selected Faculties')])
    faculty_ids = fields.Many2many("op.faculty", string="Faculties", store=True,
                                   compute="_compute_target_faculty_audience")
    created_date = fields.Date(string="Created Date",
                               default=datetime.datetime.today().date(), readonly=True)
    created_by = fields.Many2one("res.users", default=lambda self: self.env.user,
                                 readonly=True)

    @api.model_create_multi
    def create(self, vals):
        result = super(OpNoticeGroup, self).create(vals)
        if result.student_ids or result.parent_ids or result.faculty_ids:
            return result
        else:
            raise ValidationError(_(
                'Must have to Select Student or Parents or Faculty.'
            ))

    @api.depends('student_visibility', 'batch_ids')
    def _compute_target_student_audience(self):
        for group in self:
            if group.student_visibility == 'all_students':
                batches = []
                for batch in group.batch_ids:
                    batches.append(batch.id)
                group.student_ids = group.env['op.student'].search(
                    [('course_detail_ids.batch_id', 'in', batches)])
            else:
                if group.student_visibility != 'all_students':
                    # group.student_ids = None
                    group.course_ids = None
                    group.batch_ids = None

    @api.depends("parent_visibility", "parent_batch_ids")
    def _compute_target_parent_audience(self):
        for group in self:
            if group.parent_visibility == 'all_parents':
                parent_batches = []
                for parent_batch in group.parent_batch_ids:
                    parent_batches.append(parent_batch.id)
                group.parent_ids = group.env['op.parent'].search(
                    [('student_ids.course_detail_ids.batch_id', 'in', parent_batches)])
            else:
                if group.parent_visibility != 'all_parents':
                    # group.parent_ids = None
                    group.parent_course_ids = None
                    group.parent_batch_ids = None

    @api.depends("faculty_visibility")
    def _compute_target_faculty_audience(self):
        for group in self:
            if group.faculty_visibility == 'all_faculty':
                group.faculty_ids = group.env['op.faculty'].search([])
            else:
                if group.faculty_visibility != 'selected_faculty':
                    group.faculty_ids = None


class OpCourse(models.Model):
    _inherit = "op.course"

    notice_group_id = fields.Many2one("op.notice.group")


class OpBatch(models.Model):
    _inherit = "op.batch"

    notice_group_id = fields.Many2one("op.notice.group")
