# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

import uuid

from odoo import api, fields, models


class OpCourseEnrollment(models.Model):
    _name = "op.course.enrollment"
    _rec_name = "user_id"
    _description = "LMS Course Enrollment"

    index = fields.Char(string='Index', required=False, copy=False, readonly=True,
                        index=True, )
    course_id = fields.Many2one('op.course', 'Course', required=True)
    navigation_policy = fields.Selection(
        related='course_id.navigation_policy', string='Navigation Policy')
    user_id = fields.Many2one(
        'res.users', 'User', required=True, ondelete="cascade")
    enrollment_date = fields.Datetime('Enrollment Date', required=True,
                                      default=fields.Datetime.now())
    completion_date = fields.Datetime('Completion Date')
    state = fields.Selection([('draft', 'Draft'),
                              ('in_progress', 'In Progress'),
                              ('done', 'Done')],
                             'State', default='draft')
    enrollment_material_line = fields.One2many(
        'op.course.enrollment.material', 'enrollment_id',
        string='Materials')
    completed_percentage = fields.Integer(
        compute="_compute_completed_percentage",
        string="Completed Percentage", store=True)
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)
    active = fields.Boolean(default=True)

    access_url = fields.Char(
        'Portal Access URL', compute='_compute_access_url',
        help='Customer Portal URL')
    access_token = fields.Char('Security Token', copy=False)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('index', '/') == '/':
                vals['index'] = self.env['ir.sequence'] \
                                    .next_by_code('op.course.enrollment') or '/'
        return super(OpCourseEnrollment, self).create(vals_list)

    def _get_report_base_filename(self):
        self.ensure_one()
        return '%s' % (self.course_id.name)

    def _compute_access_url(self):
        for record in self:
            record.access_url = '/certificates/%s' % (record.id)

    @api.depends('course_id.training_material', 'enrollment_material_line')
    def _compute_completed_percentage(self):
        for enrollment in self:
            if not enrollment.course_id.training_material == 0:
                enrollment.completed_percentage = (len(
                    enrollment.enrollment_material_line
                ) * 100) / enrollment.course_id.training_material
            else:
                enrollment.completed_percentage = 0

    def action_onboarding_enrollment_layout(self):
        self.env.user.company_id.onboarding_enrollment_layout_state = 'done'

    def _portal_ensure_token(self):
        """ Get the current record access token """
        if not self.access_token:
            # we use a `write` to force the cache clearing otherwise
            # `return self.access_token` will return False
            self.sudo().write({'access_token': str(uuid.uuid4())})
        return self.access_token

    def get_portal_url(self, suffix=None, report_type=None,
                       download=None, query_string=None, anchor=None):
        """
            Get a portal url for this model, including access_token.
            The associated route must handle the flags for them to have any effect.
            - suffix: string to append to the url, before the query string
            - report_type: report_type query string, often one of: html, pdf, text
            - download: set the download query string to true
            - query_string: additional query string
            - anchor: string to append after the anchor #
        """
        self.ensure_one()
        url = self.access_url + '%s?access_token=%s%s%s%s%s' % (
            suffix if suffix else '',
            self._portal_ensure_token(),
            '&report_type=%s' % report_type if report_type else '',
            '&download=true' if download else '',
            query_string if query_string else '',
            '#%s' % anchor if anchor else ''
        )
        return url


class OpCourseEnrollmentMaterial(models.Model):
    _name = "op.course.enrollment.material"
    _rec_name = "enrollment_id"
    _description = "LMS Course Enrollment Material"

    enrollment_id = fields.Many2one('op.course.enrollment', 'Enrollment',
                                    ondelete='cascade')
    course_id = fields.Many2one(related='enrollment_id.course_id',
                                string='Course')
    section_id = fields.Many2one('op.course.section', 'Section')
    material_id = fields.Many2one('op.material', 'Material')
    completed = fields.Boolean('Completed')
    completed_date = fields.Datetime('Completed Time')
    last_access_date = fields.Datetime('Last Access Time')
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)
