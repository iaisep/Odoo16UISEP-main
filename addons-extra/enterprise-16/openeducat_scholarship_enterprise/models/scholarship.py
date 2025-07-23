# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import api, fields, models


class OpScholarship(models.Model):
    _name = "op.scholarship"
    _rec_name = "student_id"
    _inherit = "mail.thread"
    _description = "Scholarship"

    sponsor_id = fields.Many2one('res.partner', 'Sponsor')
    name = fields.Char(string="Name", required=True, default='New',
                       readonly=True, tracking=True)

    student_id = fields.Many2one('op.student', 'Student', required=True)
    type_id = fields.Many2one('op.scholarship.type', 'Type', required=True)
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)
    amount = fields.Integer('Amount', tracking=True)
    course_id = fields.Many2one('op.course', string='Course')
    batch_id = fields.Many2one('op.batch', string='Batch')
    active = fields.Boolean(default=True)
    scholarship_stages_id = fields.Many2one('scholarship.stages',
                                            string="Scholarship Stages",
                                            ondelete='restrict',
                                            default=lambda self:
                                            self.env.ref(
                                                "openeducat_"
                                                "scholarship_enterprise"
                                                ".op_scholarship_stages_1", False))

    bool_field = fields.Boolean('Same text', default=False)

    @api.onchange('course_id')
    def onchange_course_id(self):
        if self.course_id:
            batch_ids = self.env['op.batch'].search([
                ('course_id', '=', self.course_id.id)])
            return {'domain': {'batch_id': [('id', 'in', batch_ids.ids)]}

                    }

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'op.scholarship') or 'New'
        return super(OpScholarship, self).create(vals_list)

    def make_invoices(self):
        student = self.student_id
        for rec in self:
            self.env['op.scholarship']. \
                search([('sponsor_id', '=', rec.id)])
            invoice = self.env['account.move'].create({
                'partner_id': self.sponsor_id.id,
                'move_type': 'out_invoice',
                'invoice_date': fields.Date.today(),
                'invoice_line_ids': [(0, 0, {
                    'name': student.name,
                    'account_id': self.course_id.id,
                    'price_unit': self.amount,
                    'quantity': 1.0,
                    'discount': 0.0,
                    'product_uom_id': self.course_id.id,
                    'product_id': self.batch_id.id,
                })],
            })
            invoice._compute_always_tax_exigible()
            form_view = self.env.ref('account.view_move_form')
            tree_view = self.env.ref('account.view_invoice_tree')
            value = {
                'domain': str([('id', '=', invoice.id)]),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'account.move',
                'view_id': False,
                'views': [(form_view.id, 'form'),
                          (tree_view.id, 'tree')],
                'type': 'ir.actions.act_window',
                'res_id': invoice.id,
                'target': 'current',
                'nodestroy': True
            }
            return value
