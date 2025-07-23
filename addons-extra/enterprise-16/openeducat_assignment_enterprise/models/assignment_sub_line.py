# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import api, fields, models


class OpAssignmentSubLine(models.Model):
    _inherit = "op.assignment.sub.line"

    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)

    progression_id = fields.Many2one('op.student.progression',
                                     string="Progression No")
    attachment_ids = fields.One2many('ir.attachment', 'res_id',
                                     domain=[('res_model', '=',
                                              'op.assignment.sub.line')],
                                     string='Attachments',
                                     readonly=True)

    ignore_attempt = fields.Integer('Ignore Attempt')
    ignore = fields.Boolean('Ignore')
    state = fields.Selection(selection_add=[('ignore', 'Ignore')])

    def ignore_submission_attempt(self):
        ignore_submission = self.sudo().search([('id', '=', self.id)])
        if ignore_submission:
            self.ignore = True
        self.ignore_attempt = ignore_submission.id
        self.state = 'ignore'

    def student_submission(self):
        result = self.sudo().act_submit()
        return result and result or False

    @api.onchange('student_id')
    def onchange_student_assignment_progrssion(self):
        if self.student_id:
            student = self.env['op.student.progression'].search(
                [('student_id', '=', self.student_id.id)])
            self.progression_id = student.id
            sequence = student.name
            student.write({'name': sequence})

    def search_read_for_app(self, offset=0, limit=None, order=None):

        if self.env.user.partner_id.is_student:
            domain = [('user_id', '=', self.env.user.id)]
            fields = ['student_id', 'assignment_id', 'submission_date',
                      'state', 'description', 'note', 'marks']
            res = self.sudo().search_read(domain=domain, fields=fields,
                                          offset=offset, limit=limit, order=order)
            return res

        elif self.user_has_groups('openeducat_assignment.group_op_assignment_user'):
            fields = ['student_id', 'assignment_id', 'submission_date',
                      'state', 'description', 'note', 'marks']
            res = self.sudo().search_read(domain=[], fields=fields,
                                          offset=offset, limit=limit, order=order)
            return res
