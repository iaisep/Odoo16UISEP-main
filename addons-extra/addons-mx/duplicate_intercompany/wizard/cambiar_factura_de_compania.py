
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class CambiarFacturaDeCompania(models.TransientModel):
    _name = "cambiar.factura.de.compania"

    company_id = fields.Many2one('res.company', string = "Compañia")


    def action_crear(self):
        account_move_id =  self._context.get("default_account_move")
        if account_move_id:
            company = self.company_id
            self = self.with_company(company).with_context(company_id=company.id)
            invoice_obj = self.env["account.move"]
            account_move = invoice_obj.browse(account_move_id)
            if company and account_move.journal_id.company_id != company:
                new_journal = self.env['account.journal'].search([
                    ('type', '=', account_move.journal_id.type),
                    ('company_id', '=', company.id)
                ], limit=1)

                if not new_journal:
                    raise UserError(_('First create journal for company : %s') % (company.name))
                data = {
                    "company_id": company.id,
                    "journal_id": new_journal.id,
                    "date": account_move.date,
                    "extract_state": account_move.extract_state,
                    "move_type": account_move.move_type,
                    "auto_post": account_move.auto_post,
                    "partner_id": account_move.partner_id.id,
                    "invoice_date": account_move.invoice_date,
                    "invoice_payment_term_id": account_move.invoice_payment_term_id.id,
                    "currency_id": account_move.currency_id.id,
                    "fiscal_position_id": account_move.fiscal_position_id.id,
                }
                customer_invoice = invoice_obj.new(data)
                customer_invoice._onchange_partner_id()
                invoice_vals = customer_invoice._convert_to_write(
                    {name: customer_invoice[name] for name in customer_invoice._cache})
                move_lines = []
                for line in account_move.invoice_line_ids:
                    copied_vals = line.copy_data()[0]
                    copied_vals.pop('move_id')
                    copied_vals.pop('account_id')
                    copied_vals.pop('tax_ids')
                    copied_vals.update(
                        {
                            "move_id": customer_invoice.id,
                            "company_id": company.id,
                            "journal_id":new_journal.id,
                         }
                    )
                    move_line = self.env['account.move.line'].new(copied_vals)
                    move_line._compute_account_id()
                    move_line._compute_tax_ids()
                    move_line._inverse_product_id()
                    copy_line = move_line._convert_to_write(move_line._cache)
                    move_lines.append((0, 0, copy_line))

                if move_lines:
                    invoice_vals.update({'invoice_line_ids': move_lines})
                    if 'line_ids' in data:
                        invoice_vals.pop('line_ids')
                account_move_copy = self.env["account.move"].sudo().create(invoice_vals)
            else:
                account_move_copy = account_move.copy()

            account_move.button_draft()
            account_move.button_cancel()
#            action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_out_invoice_type")
            #action['domain'] = [('id', '=', ),]
#            action["view_type"] = "form"
#            action['view_mode'] = 'form'
#            action['res_id'] = account_move_copy.id
#            action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
#            action['context'] = {'default_move_type': 'out_invoice', 'move_type': 'out_invoice', 'journal_type': 'sale',
#                                 'search_default_unpaid': 1}
#            return action
            return





