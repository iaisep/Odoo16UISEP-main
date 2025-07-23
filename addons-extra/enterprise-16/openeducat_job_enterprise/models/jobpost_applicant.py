# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import SUPERUSER_ID, _, api, fields, models

AVAILABLE_PRIORITIES = [
    ('0', 'Normal'),
    ('1', 'Good'),
    ('2', 'Very Good'),
    ('3', 'Excellent')
]


class JobStage(models.Model):
    _name = "job.post.stage"
    _description = "Job Stages"
    _order = 'sequence'

    name = fields.Char("Stage Name", required=True, translate=True)
    sequence = fields.Integer(
        "Sequence", default=10,
        help="Gives the sequence order when displaying a list of stages.")
    post_id = fields.Many2many(
        'op.job.post', string='Job Specific',
        help='Specific jobs that uses this stage. Other'
             ' jobs will not use this stage.')
    requirements = fields.Text("Requirements")
    template_id = fields.Many2one(
        'mail.template', "Email Template",
        help="If set, a message is posted on the applicant"
             " using the template when the applicant is set to the stage.")
    fold = fields.Boolean(
        "Folded in Kanban",
        help="This stage is folded in the kanban view when"
             " there are no records in that stage to display.")
    legend_blocked = fields.Char(
        'Red Kanban Label', default=lambda self: _('Blocked'), translate=True,
        required=True)
    legend_done = fields.Char(
        'Green Kanban Label', default=lambda self: _('Ready for Next Stage'),
        translate=True, required=True)
    legend_normal = fields.Char(
        'Grey Kanban Label', default=lambda self: _('In Progress'),
        translate=True, required=True)

    @api.model
    def default_get(self, fields):
        if self._context and self._context.get('default_post_id') and not \
                self._context.get('job_post_stage_mono', False):
            context = dict(self._context)
            context.pop('default_post_id')
            self = self.with_context(context)
        return super(JobStage, self).default_get(fields)


class OpJobApplicant(models.Model):
    _name = "op.job.applicant"
    _inherit = ['mail.thread',
                'website.seo.metadata',
                'website.published.multi.mixin', 'mail.activity.mixin']
    _description = "Job Applicant"

    def _default_stage_id(self):
        if self._context.get('default_stage_id'):
            return self.env['job.post.stage']. \
                search(['|',
                        ('post_id', '=', False),
                        ('post_id', '=', self._context['default_post_id']),
                        ('fold', '=', False)], order='sequence asc',
                       limit=1).id
        return False

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        # retrieve job_id from the context and write the domain:
        # ids + contextual columns (job or default)
        post_id = self._context.get('default_post_id')

        search_domain = [('post_id', '=', False)]
        if post_id:
            search_domain = ['|', ('post_id', '=', post_id)] + search_domain
        if stages:
            search_domain = ['|', ('id', 'in', stages.ids)] + search_domain

        stage_ids = stages._search(search_domain, order=order,
                                   access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)

    name = fields.Char(string='Application Number',
                       required=True, copy=False, readonly=True,
                       index=True, default=lambda self: _('New'))
    date = fields.Date(string="Date", default=fields.Datetime.now,
                       readonly=True)
    stage_id = fields.Many2one('job.post.stage', 'Stage', ondelete='restrict',
                               tracking=True, copy=False, index=True,
                               group_expand='_read_group_stage_ids',
                               default=_default_stage_id)
    last_stage_id = fields.Many2one('job.post.stage', "Last Stage",
                                    help="Stage of the applicant"
                                         " before being in the current stage."
                                         " Used for lost cases analysis.")
    user_id = fields.Many2one('op.student', 'Name', readonly=True)
    mobile = fields.Char(related='user_id.mobile', string='mobile')
    post_id = fields.Many2one('op.job.post',
                              string='Job Post', readonly=True)
    attachment_number = fields.Integer(
        compute='_compute_get_attachment_number',
        string="Number of Attachments")
    attachment_ids = fields.One2many('ir.attachment', 'res_id',
                                     domain=[('res_model', '=',
                                              'op.job.applicant')],
                                     string='Attachments', readonly=True)
    priority = fields.Selection(AVAILABLE_PRIORITIES,
                                "Appreciation", default='0')
    create_date = fields.Datetime("Creation Date", readonly=True, index=True)
    color = fields.Integer("Color Index", default=0)
    day_open = fields.Float(compute='_compute_day',
                            string="Days to Open", compute_sudo=True)
    day_close = fields.Float(compute='_compute_day',
                             string="Days to Close", compute_sudo=True)
    date_closed = fields.Datetime("Closed", readonly=True, index=True)
    date_open = fields.Datetime("Assigned", readonly=True, index=True)
    legend_blocked = fields.Char(related='stage_id.legend_blocked',
                                 string='Kanban Blocked', readonly=False)
    legend_done = fields.Char(related='stage_id.legend_done',
                              string='Kanban Valid', readonly=False)
    legend_normal = fields.Char(related='stage_id.legend_normal',
                                string='Kanban Ongoing', readonly=False)
    date_last_stage_update = fields.Datetime("Last Stage Update", index=True,
                                             default=fields.Datetime.now)
    salary_proposed = fields.Monetary("Proposed Salary", currency_field='currency_id')
    salary_expected = fields.Monetary("Expected Salary", currency_field='currency_id')
    availability = fields.Date("Availability")
    kanban_state = fields.Selection([
        ('normal', 'Grey'),
        ('done', 'Green'),
        ('blocked', 'Red')], string='Kanban State',
        copy=False, default='normal', required=True)
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)
    active = fields.Boolean(default=True)

    @api.depends('company_id')
    def _compute_currency_id(self):
        main_company = self.env['res.company']._get_main_company()
        for template in self:
            template.currency_id = template.company_id.sudo().\
                currency_id.id or main_company.currency_id.id

    currency_id = fields.Many2one('res.currency', string='Currency',
                                  compute='_compute_currency_id',
                                  default=lambda self:
                                  self.env.user.company_id.currency_id.id)

    @api.onchange('post_id')
    def onchange_post_id(self):
        vals = self._onchange_post_id_internal(self.post_id.id)
        self.stage_id = vals['value']['stage_id']

    def _onchange_post_id_internal(self, post_id):
        stage_id = self.stage_id.id or self._context.get('default_stage_id')
        if post_id:
            job = self.env['op.job.post'].browse(post_id)
            if not stage_id:
                stage_ids = self.env['job.post.stage'].search([
                    '|',
                    ('post_id', '=', False),
                    ('post_id', '=', job.id),
                    ('fold', '=', False)
                ], order='sequence asc', limit=1).ids
                stage_id = stage_ids[0] if stage_ids else False

        return {'value': {
            'stage_id': stage_id
        }}

    @api.onchange('stage_id')
    def onchange_stage_id(self):
        vals = self._onchange_stage_id_internal(self.stage_id.id)
        if vals['value'].get('date_closed'):
            self.date_closed = vals['value']['date_closed']

    def _onchange_stage_id_internal(self, stage_id):
        if not stage_id:
            return {'value': {}}
        stage = self.env['job.post.stage'].browse(stage_id)
        if stage.fold:
            return {'value': {'date_closed': fields.datetime.now()}}
        return {'value': {'date_closed': False}}

    @api.depends('date_open', 'date_closed')
    def _compute_day(self):
        for applicant in self:
            if applicant.date_open:
                date_create = applicant.create_date
                date_open = applicant.date_open
                applicant.day_open = (date_open - date_create). \
                    total_seconds() / (24.0 * 3600)
            else:
                applicant.day_open = False
            if applicant.date_closed:
                date_create = applicant.create_date
                date_closed = applicant.date_closed
                applicant.day_close = (date_closed - date_create). \
                    total_seconds() / (24.0 * 3600)
            else:
                applicant.day_close = False

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', '/') == '/':
                vals['name'] = self.env['ir.sequence']. \
                    next_by_code('op.job.applicant') or '/'
        return super(OpJobApplicant, self).create(vals_list)

    def _compute_get_attachment_number(self):
        read_group_res = self.env['ir.attachment'].read_group(
            [('res_model', '=', 'op.job.applicant'),
             ('res_id', 'in', self.ids)],
            ['res_id'], ['res_id'])
        attach_data = {res['res_id']:
                       res['res_id_count'] for res in read_group_res}
        for record in self:
            record.attachment_number = attach_data.get(record.id, 0)

    def action_get_attachment_tree_view(self):
        attachment_action = self.env.ref('base.action_attachment')
        action = attachment_action.read()[0]
        action['context'] = {'default_res_model': self._name,
                             'default_res_id': self.ids[0]}
        action['domain'] = str(['&', ('res_model', '=', self._name),
                                ('res_id', 'in', self.ids)])
        return action

    def write(self, vals):
        # user_id change: update date_open
        if vals.get('user_id'):
            vals['date_open'] = fields.Datetime.now()
        # stage_id: track last stage before update
        if 'stage_id' in vals:
            vals['date_last_stage_update'] = fields.Datetime.now()
            vals.update(self._onchange_stage_id_internal(vals.get('stage_id'))
                        ['value'])
            if 'kanban_state' not in vals:
                vals['kanban_state'] = 'normal'
            for applicant in self:
                vals['last_stage_id'] = applicant.stage_id.id
                res = super(OpJobApplicant, self).write(vals)
        else:
            res = super(OpJobApplicant, self).write(vals)
        return res


class OpStudent(models.Model):
    _inherit = "op.student"

    job_post_ids = fields.One2many(
        'op.job.applicant', 'user_id', 'Job Post Details')

    Job_post_count = fields.Integer(compute='_compute_count_job_post')

    def get_job_post(self):
        action = self.env.ref('openeducat_job_enterprise.'
                              'act_open_job_applicant_view').read()[0]
        action['domain'] = [('user_id', 'in', self.ids)]
        return action

    def _compute_count_job_post(self):
        for record in self:
            record.Job_post_count = self.env['op.job.applicant'].search_count(
                [('user_id', 'in', self.ids)])
