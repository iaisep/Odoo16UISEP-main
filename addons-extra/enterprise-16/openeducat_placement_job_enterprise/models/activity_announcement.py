# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import fields, models


class OpActivityAnnouncement(models.Model):
    _name = "op.activity.announcement"
    _inherit = ["mail.thread",
                'website.seo.metadata',
                'website.published.multi.mixin']
    _description = "Activity Announcement Creation"

    name = fields.Char(string='Name', required=True)
    partner_id = fields.Many2one("res.partner", "Organisation",
                                 tracking=True)
    team_id = fields.Many2one('op.placement.cell', string='Handled By',
                              tracking=True)
    job_post_id = fields.Many2many('op.job.post',
                                   string='Job Post',
                                   domain="[('states','=','submit')]",
                                   tracking=True)
    skill_id = fields.Many2many('op.student.skill.name', string='Required Skills')
    start_date = fields.Date(
        'Start Date', required=True, default=fields.Date.today(),
        tracking=True)
    end_date = fields.Date('End Date', required=True,
                           tracking=True)
    description = fields.Text('Description', translate=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('closed', 'Closed')], default='draft')
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)
    active = fields.Boolean(default=True)

    def set_draft(self):
        self.state = "draft"

    def set_open(self):
        self.state = "open"

    def set_closed(self):
        self.state = "closed"

    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'state' in init_values and self.state == 'closed':
            return 'openeducat_placement_job_enterprise.activity_closed'
        elif 'state' in init_values and self.state == 'open':
            return 'openeducat_placement_job_enterprise.activity_open'
        elif 'state' in init_values and self.state == 'draft':
            return 'openeducat_placement_job_enterprise.activity_draft'
        return super(OpActivityAnnouncement, self)._track_subtype(init_values)

    def _compute_website_url(self):
        super(OpActivityAnnouncement, self)._compute_website_url()
        for job in self:
            job.website_url = "/activity/announcement/apply/%s" % job.id
