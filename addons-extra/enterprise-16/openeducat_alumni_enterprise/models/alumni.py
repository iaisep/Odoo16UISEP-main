# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import _, fields, models
from odoo.exceptions import UserError


class OpAlumni(models.Model):
    _inherit = "op.student"

    alumni_boolean = fields.Boolean('Alumni Student')
    passing_year_id = fields.Many2one('op.batch', 'Passing Year')
    current_position = fields.Char('Current Position', size=256)
    current_job = fields.Char('Current Job', size=256)

    alumni_id = fields.Many2one('op.alumni.group', string='Group')
    invoice_id = fields.Many2one('account.move', 'Invoice ID')
    number = fields.Char(related='invoice_id.name', string='Invoice Number')
    join_date = fields.Date(related='invoice_id.invoice_date',
                            string="Join Date")

    state = fields.Selection([
        ('draft', 'Draft'),
        ('invoice', 'Invoice Created'),
        ('cancel', 'Cancel')
    ], string='Status')

    def get_invoice(self):
        """ Create invoice for fee payment process of student """
        inv_obj = self.env['account.move']
        account_id = False
        product = self.alumni_id.fees_id

        if product.property_account_income_id:
            account_id = product.property_account_income_id.id
        if not account_id:
            account_id = product.categ_id.property_account_income_categ_id.id
        if not account_id:
            raise UserError(
                _('There is no income account defined for this product: "%s".'
                  'You may have to install a chart of account from Accounting'
                  ' app, settings menu.') % product.name)
        if self.alumni_id.alumni_fees_amount <= 0.00:
            raise UserError(
                _('The value of the deposit amount must be positive.'))

        invoice = inv_obj.create({
            'name': self.name,
            'move_type': 'out_invoice',
            'partner_id': self.partner_id.id,

        })
        element_id = self.env['op.alumni.group'].search([
            ('name', '=', self.alumni_id.name)])
        for records in element_id:

            if records:
                line_values = {'name': records.name,
                               'account_id': account_id,
                               'price_unit': records.alumni_fees_amount,
                               'quantity': 1.0,
                               'discount': 0.0,
                               'product_uom_id': records.fees_id.uom_id.id,
                               'product_id': records.fees_id.id, }
                invoice.write({'invoice_line_ids': [(0, 0, line_values)]})

        invoice._compute_always_tax_exigible()
        self.state = 'invoice'
        self.invoice_id = invoice.id
        return True

    def action_get_invoice(self):
        value = True
        if self.invoice_id:
            form_view = self.env.ref('account.view_move_form')
            tree_view = self.env.ref('account.view_invoice_tree')
            value = {
                'domain': str([('id', '=', self.invoice_id.id)]),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'account.move',
                'view_id': False,
                'views': [(form_view and form_view.id or False, 'form'),
                          (tree_view and tree_view.id or False, 'tree')],
                'type': 'ir.actions.act_window',
                'res_id': self.invoice_id.id,
                'target': 'current',
                'nodestroy': True
            }
        return value
