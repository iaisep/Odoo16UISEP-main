# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

import datetime

from odoo import _, api, fields, models


class OpCircular(models.Model):
    _name = "op.circular"
    _inherit = ['mail.thread.cc', 'mail.activity.mixin']
    _description = "Circular"

    name = fields.Char(string="Name", required=True)
    subject = fields.Char(string="Subject", required=True)
    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date")
    description = fields.Html(string="Description", required=True)
    circular_number = fields.Char(string="Circular Number", default="New")
    group_id = fields.Many2one("op.notice.group", string="Group", required=True)
    created_by = fields.Many2one("res.users", string="Created By",
                                 default=lambda self: self.env.user, readonly=True)
    created_date = fields.Date(string="Created Date",
                               default=datetime.datetime.today().date(), readonly=True)
    academic_year_id = fields.Many2one('op.academic.year',
                                       string='Academic Year', required=True)
    academic_term_id = fields.Many2one('op.academic.term',
                                       string='Academic Terms', required=True)
    state = fields.Selection([('draft', 'Draft'),
                              ('in_progress', 'In Progress'),
                              ('publish', 'Published'),
                              ('cancel', 'Canceled'),
                              ('unpublish', 'Unpublished')],
                             string="Status", default='draft')
    high_priority = fields.Selection(
        [('3', 'Low'), ('2', 'Normal'), ('1', 'High')],
        string='Priority', default='3')
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('circular_number', 'New') == 'New':
                vals['circular_number'] = self.env['ir.sequence']\
                                              .next_by_code('op.circular') or 'New'
        result = super(OpCircular, self).create(vals_list)
        return result

    def action_in_progress(self):
        self.state = 'in_progress'

    def action_publish(self):
        self.state = 'publish'

    def action_cancel(self):
        self.state = 'cancel'

    def action_unpublish(self):
        self.state = 'unpublish'

    def action_draft(self):
        self.state = 'draft'

    def _composer_format(self, res_model, res_id, template):
        compose_form = self.env.ref(
            'mail.email_compose_message_wizard_form', False)
        ctx = dict(
            default_model=res_model,
            default_res_id=res_id,
            default_use_template=bool(template),
            default_template_id=template and template.id or False,
            default_composition_mode='comment',
            force_email=True
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

    def circular_action_send_email(self):
        self.ensure_one()
        template = self.env.ref('openeducat_notice_board_enterprise.'
                                'email_circular_template', raise_if_not_found=False)

        return self._composer_format(res_model='op.circular',
                                     res_id=self.id,
                                     template=template)
