# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import fields, models


class StudentProgression(models.Model):
    _name = "op.student.progression"
    _description = "Student progression"
    _inherit = ["mail.thread"]

    name = fields.Char('Sequence',
                       default=lambda self: self.env['ir.sequence'].
                       next_by_code('op.student.progression'),
                       copy=False, required=True)
    student_id = fields.Many2one('op.student',
                                 'Student', required=True,
                                 tracking=True)
    created_by = fields.Many2one('res.users', 'Created By',
                                 readonly=True,
                                 default=lambda self: self.env.uid,
                                 tracking=True)
    date = fields.Date('Date',
                       required=True,
                       default=fields.Date.today(),
                       tracking=True)

    state = fields.Selection([('draft', 'Draft'),
                              ('open', 'In Progress'),
                              ('done', 'Done'),
                              ('cancel', 'Cancel')],
                             string="Status", default='draft',
                             tracking=True)
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)
    active = fields.Boolean(default=True)

    def state_draft(self):
        self.state = "draft"

    def state_open(self):
        self.state = "open"

    def state_done(self):
        self.state = "done"

    def state_rejected(self):
        self.state = "cancel"

    _sql_constraints = [('student_id',
                         'unique(student_id)',
                         'Student already  exist!!!')]
