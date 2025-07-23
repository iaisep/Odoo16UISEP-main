# -*- coding: utf-8 -*-
import logging
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from werkzeug import urls
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons.payment import utils as payment_utils

from odoo.tools import config, split_every
from odoo.osv import expression
from psycopg2.extensions import TransactionRollbackError
from odoo.tools.float_utils import float_is_zero
from odoo.tools.date_utils import get_timedelta

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    

    invoice_schedule_done = fields.Boolean(string='Facturación programada completa', default=False)

    def _recurring_invoice_domain_update(self, extra_domain=None):
        num_day = int(self.env['ir.config_parameter'].sudo().get_param('num_day'))
        if not extra_domain:
            extra_domain = []
        current_date = fields.Date.today() + timedelta(days=num_day)
        search_domain = [('is_batch', '=', False),
                         ('is_invoice_cron', '=', False),
                         ('is_subscription', '=', True),
                         ('subscription_management', '!=', 'upsell'),
                         ('state', 'in', ['sale', 'done']), # allow to close done subscription at the beginning of the invoicing cron
                         ('payment_exception', '=', False),
                         '&', '|', ('next_invoice_date', '<=', current_date), ('end_date', '<=', current_date), ('stage_category', '=', 'progress')]
        if extra_domain:
            search_domain = expression.AND([search_domain, extra_domain])
        return search_domain



    @api.model
    def cron_recurring_create_invoice_update(self):
        return self._create_recurring_invoice_update(automatic=True)


    def _get_invoiceable_lines(self, final=False):
        num_day = int(self.env['ir.config_parameter'].sudo().get_param('num_day'))
        date_from = fields.Date.today() + timedelta(days=num_day)
        res = super()._get_invoiceable_lines(final=final)
        res = res.filtered(lambda l: l.temporal_type != 'subscription' or l.order_id.subscription_management == 'upsell')
        automatic_invoice = self.env.context.get('recurring_automatic')

        invoiceable_line_ids = []
        downpayment_line_ids = []
        pending_section = None

        for line in self.order_line:
            if line.display_type == 'line_section':
                # Only add section if one of its lines is invoiceable
                pending_section = line
                continue

            time_condition = line.order_id.next_invoice_date and line.order_id.next_invoice_date <= date_from  and line.order_id.start_date and line.order_id.start_date <= date_from
            line_condition = time_condition or not automatic_invoice # automatic mode force the invoice when line are not null
            line_to_invoice = False
            if line in res:
                # Line was already marked as to be invoiced
                line_to_invoice = True
            elif line.order_id.subscription_management == 'upsell':
                # Super() already select everything that is needed for upsells
                line_to_invoice = False
            elif line.display_type or line.temporal_type != 'subscription':
                # Avoid invoicing section/notes or lines starting in the future or not starting at all
                line_to_invoice = False
            elif line_condition and line.product_id.invoice_policy == 'order' and line.order_id.state == 'sale':
                # Invoice due lines
                line_to_invoice = True
            elif line_condition and line.product_id.invoice_policy == 'delivery' and (not float_is_zero(line.qty_delivered, precision_rounding=line.product_id.uom_id.rounding)):
                line_to_invoice = True

            if line_to_invoice:
                if line.is_downpayment:
                    # downpayment line must be kept at the end in its dedicated section
                    downpayment_line_ids.append(line.id)
                    continue
                if pending_section:
                    invoiceable_line_ids.append(pending_section.id)
                    pending_section = False
                invoiceable_line_ids.append(line.id)

        return self.env["sale.order.line"].browse(invoiceable_line_ids + downpayment_line_ids)




    def _create_recurring_invoice_update(self, automatic=False, batch_size=30):
        num_day = int(self.env['ir.config_parameter'].sudo().get_param('num_day'))
        automatic = bool(automatic)
        auto_commit = automatic and not bool(config['test_enable'] or config['test_file'])
        Mail = self.env['mail.mail']
        today = fields.Date.today() + timedelta(days=num_day)
        invoiceable_categories = ['progress']
        if len(self) > 0:
            all_subscriptions = self.filtered(lambda so: so.is_subscription and so.subscription_management != 'upsell' and not so.payment_exception)
            need_cron_trigger = False
            invoiceable_categories.append('paused')
        else:
            search_domain = self._recurring_invoice_domain_update()
            all_subscriptions = self.search(search_domain, limit=batch_size + 1)
            need_cron_trigger = len(all_subscriptions) > batch_size
            if need_cron_trigger:
                all_subscriptions = all_subscriptions[:batch_size]
        if not all_subscriptions:
            return self.env['account.move']
        # don't spam sale with assigned emails.
        all_subscriptions = all_subscriptions.with_context(mail_auto_subscribe_no_notify=True)
        auto_close_subscription = all_subscriptions.filtered_domain([('end_date', '!=', False)])
        all_invoiceable_lines = all_subscriptions.with_context(recurring_automatic=automatic)._get_invoiceable_lines(final=False)

        auto_close_subscription._subscription_auto_close_and_renew()
        if automatic:
            all_subscriptions.write({'is_invoice_cron': True})
        lines_to_reset_qty = self.env['sale.order.line'] # qty_delivered is set to 0 after invoicing for some categories of products (timesheets etc)
        account_moves = self.env['account.move']
        # Set quantity to invoice before the invoice creation. If something goes wrong, the line will appear as "to invoice"
        # It prevent to use the _compute method and compare the today date and the next_invoice_date in the compute.
        # That would be bad for perfs
        all_invoiceable_lines._reset_subscription_qty_to_invoice()
        if auto_commit:
            self.env.cr.commit()
        for subscription in all_subscriptions:
            # We only invoice contract in sale state. Locked contracts are invoiced in advance. They are frozen.
            if not (subscription.state == 'sale' and subscription.stage_category in invoiceable_categories):
                continue
            try:
                subscription = subscription[0] # Trick to not prefetch other subscriptions, as the cache is currently invalidated at each iteration
                # in rare occurrences (due to external issues not related with Odoo), we may have
                # our crons running on multiple workers thus doing work in parallel
                # to avoid processing a subscription that might already be processed
                # by a different worker, we check that it has not already been set to "in exception"
                if subscription.payment_exception:
                    continue
                if auto_commit:
                    self.env.cr.commit() # To avoid a rollback in case something is wrong, we create the invoices one by one
                draft_invoices = subscription.invoice_ids.filtered(lambda am: am.state == 'draft')
                if not subscription.payment_token_id and draft_invoices:
                    if not automatic:
                        raise UserError(_("There is already a draft invoice for subscription %s.", subscription.name))
                    # Skip subscription if no payment_token, and it has a draft invoice
                    continue
                if subscription.payment_token_id:
                    draft_invoices.button_cancel()
                invoiceable_lines = all_invoiceable_lines.filtered(lambda l: l.order_id.id == subscription.id)
                invoice_is_free, is_exception = subscription._invoice_is_considered_free(invoiceable_lines)
                if not invoiceable_lines or invoice_is_free:
                    if is_exception and automatic:
                        # Mix between recurring and non-recurring lines. We let the contract in exception, it should be
                        # handled manually
                        msg_body = _(
                            "Mix of negative recurring lines and non-recurring line. The contract should be fixed manually",
                            inv=self.next_invoice_date
                        )
                        subscription.message_post(body=msg_body)
                        subscription.payment_exception = True
                    # We still update the next_invoice_date if it is due
                    elif not automatic or subscription.next_invoice_date <= today:
                        subscription._update_next_invoice_date()
                        if invoice_is_free:
                            for line in invoiceable_lines:
                                line.qty_invoiced = line.product_uom_qty
                            subscription._subscription_post_success_free_renewal()
                    if auto_commit:
                        self.env.cr.commit()
                    continue
                try:
                    invoice = subscription.with_context(recurring_automatic=automatic)._create_invoices()
                    lines_to_reset_qty |= invoiceable_lines
                except Exception as e:
                    if auto_commit:
                        self.env.cr.rollback()
                    elif isinstance(e, TransactionRollbackError) or not automatic:
                        # the transaction is broken we should raise the exception
                        raise
                    # we suppose that the payment is run only once a day
                    email_context = subscription._get_subscription_mail_payment_context()
                    error_message = _("Error during renewal of contract %s (Payment not recorded)", subscription.name)
                    _logger.exception(error_message)
                    mail = Mail.sudo().create({'body_html': error_message, 'subject': error_message, 'email_to': email_context['responsible_email'], 'auto_delete': True})
                    mail.send()
                    continue
                if auto_commit:
                    self.env.cr.commit()
                # Handle automatic payment or invoice posting
                if automatic:
                    existing_invoices = subscription._handle_automatic_invoices(auto_commit, invoice)
                    account_moves |= existing_invoices
                else:
                    account_moves |= invoice
                subscription.with_context(mail_notrack=True).write({'payment_exception': False})
            except Exception as error:
                _logger.exception("Error during renewal of contract %s", subscription.client_order_ref or subscription.name)
                if auto_commit:
                    self.env.cr.rollback()
                if not automatic:
                    raise error
            else:
                if auto_commit:
                    self.env.cr.commit()
        lines_to_reset_qty._reset_subscription_quantity_post_invoice()
        all_subscriptions._process_invoices_to_send(account_moves, auto_commit)
        # There is still some subscriptions to process. Then, make sure the CRON will be triggered again asap.
        if need_cron_trigger:
            if config['test_enable'] or config['test_file']:
                # Test environnement: we launch the next iteration in the same thread
                self.env['sale.order']._create_recurring_invoice_update(automatic, batch_size)
            else:
                self.env.ref('isep_sale_order_cron_payment.account_analytic_cron_for_invoice_payment')._trigger()

        if automatic and not need_cron_trigger:
            cron_subs = self.search([('is_invoice_cron', '=', True)])
            cron_subs.write({'is_invoice_cron': False})

        if not need_cron_trigger:
            failing_subscriptions = self.search([('is_batch', '=', True)])
            failing_subscriptions.write({'is_batch': False})

        return account_moves

    def cron_generate_subscription_schedule_invoices(self):
        today = date(2024, 3, 1)
        batch_size = 1000
        subscriptions = self.search([
            ('is_subscription', '=', True),
            ('state', '=', 'sale'),
            ('stage_id.autogenerate_subs_invoices', '=', True),
            ('invoice_schedule_done', '=', False),
            ('amount_total', '>', 0)
        ], limit=batch_size)
        AccountMove = self.env['account.move']

        for subscription in subscriptions:
            try:
                for schedule_line in subscription.subscription_schedule:
                    if schedule_line.invoice_ids and schedule_line.payment_state != 'not_paid':
                        continue
                    if schedule_line.date_due and schedule_line.date_due >= today:

                        total_invoiced = schedule_line.total_invoiced or 0.0
                        expected = schedule_line.amount_recurring_taxinc or 0.0

                        if round(total_invoiced, 2) >= round(expected, 2):
                            continue

                        remaining = expected - total_invoiced
                        invoice_vals = subscription._prepare_invoice_from_schedule_line(schedule_line, remaining)                    
                        # Verificar si hay líneas para facturar
                        if not invoice_vals or not invoice_vals.get('invoice_line_ids'):
                            continue
                            
                        invoice_vals['invoice_origin'] = subscription.name
                        invoice = AccountMove.create(invoice_vals)
                        invoice.action_post()
                        schedule_line.invoice_ids = [(4, invoice.id)]
                        subscription.next_invoice_date = subscription.end_date + relativedelta(days=30)
                all_lines_done = all(
                    (schedule_line.payment_state != 'not_paid') or
                    (round(schedule_line.total_invoiced or 0.0, 2) >= round(schedule_line.amount_recurring_taxinc or 0.0, 2))
                    for schedule_line in subscription.subscription_schedule
                )
                if all_lines_done:
                    subscription.invoice_schedule_done = True

            except Exception as e:
                _logger = logging.getLogger(__name__)
                _logger.error(f"Error al procesar la suscripción {subscription.name}: {str(e)}")
                #dejar mensaje en el chatter para seguimiento
                subscription.message_post(
                    body=f"Error al generar factura de suscripción: {str(e)}",
                    subtype_xmlid="mail.mt_note"
                )
                continue
                    
    def _prepare_invoice_from_schedule_line(self, schedule_line, remaining_amount):
        self.ensure_one()
        num_day = int(self.env['ir.config_parameter'].sudo().get_param('num_day')) 
        journal = self.env['account.journal'].search([
            ('type', '=', 'sale'),
            ('company_id', '=', self.company_id.id)
        ], limit=1)

        if not journal:
            return

        invoice_date = schedule_line.date_due - timedelta(days=num_day) if schedule_line.date_due else fields.Date.today()

        invoice_vals = {
            'move_type': 'out_invoice',
            'partner_id': self.partner_invoice_id.id,
            'invoice_origin': self.name,
            'payment_reference': self.name,
            'ref': self.name,
            'invoice_user_id': self.user_id.id,
            'invoice_date': schedule_line.date_due,
            'invoice_date_due': invoice_date,
            'invoice_payment_term_id': False,
            'currency_id': self.currency_id.id,
            'journal_id': journal.id,
            'invoice_line_ids': [],
            'order_subscription_id': self.id,
            'company_id': self.company_id.id,
            'campaign_id': self.campaign_id.id,
            'medium_id': self.medium_id.id,
            'source_id': self.source_id.id,
            'team_id': self.team_id.id,
            'user_id': self.user_id.id,
        }

        previous_invoices = schedule_line.invoice_ids
        

        is_first_invoice = not previous_invoices or all(inv.state == 'cancel' for inv in previous_invoices)


        for line in self.order_line:

            is_recurring = line.product_id.recurring_invoice
            

            if not is_recurring and not is_first_invoice:
                continue
                

            line_total = line.price_unit * line.product_uom_qty
            

            invoiced_amount = 0.0
            for invoice in previous_invoices:
                if invoice.state != 'cancel':
                    for inv_line in invoice.invoice_line_ids:

                        if line.id in inv_line.sale_line_ids.ids:
                            invoiced_amount += inv_line.price_unit * inv_line.quantity

            remaining_for_line = line_total - invoiced_amount
            

            if remaining_for_line:  
                invoice_vals['invoice_line_ids'].append((0, 0, {
                    'product_id': line.product_id.id,
                    'name': line.name,
                    'quantity': line.product_uom_qty,
                    'product_uom_id': line.product_uom.id,
                    'price_unit': remaining_for_line / line.product_uom_qty if remaining_for_line / line.product_uom_qty > 0 else line.price_unit, 
                    'tax_ids': [(6, 0, line.tax_id.ids)],
                    'sale_line_ids': [(6, 0, [line.id])],
                }))
 
        if not invoice_vals['invoice_line_ids']:
            return None
        
        return invoice_vals
        
class SaleOrderStage(models.Model):
    _inherit = 'sale.order.stage'
        
    autogenerate_subs_invoices = fields.Boolean(string='Autogenerar facturas de suscripción')

