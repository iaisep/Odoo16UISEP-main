# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import api, fields, models


class OpPlacementOffer(models.Model):
    _name = "op.placement.offer"
    _inherit = "mail.thread"
    _description = "Placement Offer"

    name = fields.Char('Company Name', required=True)
    student_id = fields.Many2one('op.student', 'Student Name', required=True)
    join_date = fields.Date('Join Date', default=fields.Date.today())
    offer_package = fields.Monetary(
        'Offered Package', currency_field='currency_id')
    training_period = fields.Char('Training Period', default=256)
    state = fields.Selection(
        [('draft', 'Draft'), ('offer', 'Offer'), ('join', 'Join'),
         ('reject', 'Rejected'), ('cancel', 'Cancel')], 'State',
        default='draft', tracking=True)
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)

    @api.depends('company_id')
    def _compute_currency_id(self):
        main_company = self.env['res.company']._get_main_company()
        for template in self:
            template.currency_id = template.company_id.sudo(
            ).currency_id.id or main_company.currency_id.id

    currency_id = fields.Many2one('res.currency',
                                  string='Currency',
                                  compute='_compute_currency_id',
                                  default=lambda self:
                                  self.env.user.company_id.currency_id.id)

    def placement_offer(self):
        self.state = 'offer'

    def placement_join(self):
        self.state = 'join'

    def confirm_rejected(self):
        self.state = 'reject'

    def confirm_to_draft(self):
        self.state = 'draft'

    def confirm_cancel(self):
        self.state = 'cancel'


class OpStudent(models.Model):
    _inherit = "op.student"

    placement_line = fields.One2many(
        'op.placement.offer', 'student_id', 'Placement Details')

    placement_count = fields.Integer(compute='_compute_placement_count')

    def get_placement(self):
        action = self.env.ref('openeducat_placement_enterprise.'
                              'act_open_op_placement_offer_view').read()[0]
        action['domain'] = [('student_id', 'in', self.ids)]
        return action

    def _compute_placement_count(self):
        for record in self:
            record.placement_count = self.env['op.placement.offer'].search_count(
                [('student_id', 'in', self.ids)])
