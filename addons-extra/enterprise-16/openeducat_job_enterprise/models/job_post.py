# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class OpPlacementOffer(models.Model):
    _name = "op.job.post"
    _inherit = ['mail.thread',
                'website.seo.metadata',
                'website.published.multi.mixin']
    _description = "Job Post Creation"
    name = fields.Char(string='Name', required=True, copy=False, readonly=True,
                       index=True, default=lambda self: _('New'))
    job_post = fields.Char(string='Job Position',
                           tracking=True,
                           required=True, index=True,
                           translate=True)
    street = fields.Char("Address", required=True)
    street2 = fields.Char(required=True)
    city = fields.Char(required=True)
    zip = fields.Char()
    country_id = fields.Many2one('res.country')
    state_id = fields.Many2one("res.country.state",
                               domain="[('country_id', '=', country_id)]")
    employment_type = fields.Many2one("op.job.type", string="Employment Type")
    description = fields.Text('Description', translate=True)
    expected_employees = fields.Integer(string='Estimated New Employees')
    salary_from = fields.Monetary("Salary From",
                                  tracking=True, required=True,
                                  currency_field='currency_id')
    salary_upto = fields.Monetary("Salary Upto",
                                  tracking=True, required=True,
                                  currency_field='currency_id')
    payable_at = fields.Selection(
        [('weekly', 'Weekly'),
         ('monthly', 'Monthly'),
         ('yearly', 'Yearly')], tracking=True, string='Payable At')
    start_date = fields.Date('Start Date',
                             required=True, tracking=True)
    end_date = fields.Date('End Date',
                           required=True, tracking=True)
    color = fields.Integer("Color Index")
    states = fields.Selection([
        ('draft', 'Draft'),
        ('review', 'review'),
        ('submit', 'Recruitment in Progress'),
        ('done', 'Not Recruiting'),
        ('cancel', 'cancel')], default='draft')
    created_by = fields.Selection(
        [('placement', 'Placement Team'),
         ('alumni', 'Alumni')], tracking=True, string='Created By')
    application_count = fields.Integer(compute='_compute_application_count',
                                       string="Application Count")
    new_application_count = fields.Integer(
        compute='_compute_new_application_count', string="New Application",
        help="Number of applications that are new in the flow (typically at"
             " first step of the flow)")
    post = fields.Many2one("op.job.applicant", string="post")
    no_of_recruitment = fields.Integer(string='Expected New Employees',
                                       copy=False,
                                       help='Number of new employees you'
                                            ' expect to recruit.', default=1)
    department_id = fields.Many2one(
        'op.department', 'Department',
        default=lambda self:
        self.env.user.dept_id and self.env.user.dept_id.id or False)
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)

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
    active = fields.Boolean(default=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', '/') == '/':
                vals['name'] = self.env['ir.sequence'] \
                                   .next_by_code('op.job.post') or '/'
        return super(OpPlacementOffer, self).create(vals_list)

    @api.constrains('start_date', 'end_date')
    def check_dates(self):
        for record in self:
            start_date = fields.Date.from_string(record.start_date)
            end_date = fields.Date.from_string(record.end_date)
        if end_date < start_date:
            raise ValidationError(
                _("End Date cannot be set before Start Date."))

    def set_draft(self):
        self.states = "draft"

    def set_review(self):
        self.states = "review"

    def set_submit(self):
        self.states = "submit"

    def set_done(self):
        self.states = "done"

    def set_cancel(self):
        self.states = "cancel"

    def _compute_application_count(self):
        read_group_result = self.env['op.job.applicant']. \
            read_group([('post_id', 'in', self.ids)], ['post_id'], ['post_id'])
        result = {data['post_id'][0]: data['post_id_count']
                  for data in read_group_result}
        for job in self:
            job.application_count = result.get(job.id, 0)

    def _compute_new_application_count(self):
        for job in self:
            job.new_application_count = self.env["op.job.applicant"]. \
                search_count(
                [("post_id", "=", job.id),
                 ("stage_id", "=", job._get_first_stage().id)]
            )

    def _get_first_stage(self):
        self.ensure_one()
        return self.env['job.post.stage'].search([
            '|',
            ('post_id', '=', False),
            ('post_id', '=', self.id)], order='sequence asc', limit=1)

    def _compute_website_url(self):
        super(OpPlacementOffer, self)._compute_website_url()
        for job in self:
            job.website_url = "/job_post/detail/post/%s" % job.id

    def set_recruit(self):
        for record in self:
            no_of_recruitment = 1 if record.no_of_recruitment == 0 else \
                record.no_of_recruitment
            record.write({'states': 'review',
                          'no_of_recruitment': no_of_recruitment})
        return True
