import logging
from dateutil.relativedelta import relativedelta
from odoo import fields, models, _, api, Command, SUPERUSER_ID
_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"


    #overwrite method
    def _handle_automatic_invoices(self, auto_commit, invoices):
        """ This method handle the subscription with or without payment token """
        Mail = self.env['mail.mail']
        automatic_values = self._get_automatic_subscription_values()
        existing_invoices = invoices
        for order in self:
            invoice = invoices.filtered(lambda inv: inv.invoice_origin == order.name)
            email_context = order._get_subscription_mail_payment_context()
            # Set the contract in exception. If something go wrong, the exception remains.
            order.with_context(mail_notrack=True).write({'payment_exception': True})
            if not order.payment_token_id:
                invoice.action_post()
            else:
                payment_callback_done = False
                try:
                    payment_token = order.payment_token_id
                    transaction = None
                    # execute payment
                    if payment_token:
                        if not payment_token.partner_id.country_id:
                            msg_body = 'Automatic payment failed. Contract set to "To Renew". No country specified on payment_token\'s partner'
                            order.message_post(body=msg_body)
                            order.with_context(mail_notrack=True).write(automatic_values)
                            if auto_commit:
                                self.env.cr.commit()
                            continue
                        transaction = order._do_payment(payment_token, invoice)
                        payment_callback_done = transaction and transaction.sudo().callback_is_done
                        # commit change as soon as we try the payment, so we have a trace in the payment_transaction table
                        if auto_commit:
                            self.env.cr.commit()
                    # if transaction is a success, post a message
                    if transaction and transaction.state == 'done':
                        order.with_context(mail_notrack=True).write({'payment_exception': False})
                        self._subscription_post_success_payment(invoice, transaction)
                        if auto_commit:
                            self.env.cr.commit()
                    # if no transaction or failure, log error, rollback and remove invoice
                    if transaction and not transaction.renewal_allowed:
                        if auto_commit:
                            # prevent rollback during tests
                            self.env.cr.rollback()
                        order._handle_subscription_payment_failure(invoice, transaction, email_context)
                        if auto_commit:
                            self.env.cr.commit()
                        if invoice.state == 'draft':
                            invoice.action_post()
                except Exception:
                    if auto_commit:
                        # prevent rollback during tests
                        self.env.cr.rollback()
                    # we suppose that the payment is run only once a day
                    last_transaction = self.env['payment.transaction'].search(['|',
                                                                               ('reference', 'like',
                                                                                order.client_order_ref),
                                                                               ('reference', 'like', order.name)
                                                                               ], limit=1)
                    error_message = "Error during renewal of contract [%s] %s (%s)" \
                                    % (order.id, order.client_order_ref or order.name,
                                       'Payment recorded: %s' % last_transaction.reference
                                       if last_transaction and last_transaction.state == 'done' else 'Payment not recorded')
                    _logger.exception(error_message)
                    mail = Mail.sudo().create({'body_html': error_message, 'subject': error_message,
                                        'email_to': email_context.get('responsible_email'), 'auto_delete': True})
                    mail.send()

        return existing_invoices

    def _handle_subscription_payment_failure(self, invoice, transaction, email_context):
        self.ensure_one()
        current_date = fields.Date.today()
        reminder_mail_template = self.env.ref('sale_subscription.email_payment_reminder', raise_if_not_found=False)
        close_mail_template = self.env.ref('sale_subscription.email_payment_close', raise_if_not_found=False)
        auto_close_days = self.sale_order_template_id.auto_close_limit or 15
        date_close = self.next_invoice_date + relativedelta(days=auto_close_days)
        close_contract = current_date >= date_close
        _logger.info('Failed to create recurring invoice for contract %s', self.client_order_ref or self.name)
        if close_contract:
            close_mail_template.with_context(email_context).send_mail(self.id)
            _logger.debug("Sending Contract Closure Mail to %s for contract %s and closing contract",
                          self.partner_id.email, self.id)
            msg_body = 'Automatic payment failed after multiple attempts. Contract closed automatically.'
            self.message_post(body=msg_body)
            subscription_values = {'end_date': current_date, 'payment_exception': False}
            # close the contract as needed
            self.set_close()
        else:
            msg_body = 'Automatic payment failed. Contract set to "To Renew". No email sent this time. Error: %s' % (
                    transaction and transaction.state_message or 'No valid Payment Method')

            if (fields.Date.today() - self.next_invoice_date).days in [2, 7, 14]:
                email_context.update({'date_close': date_close, 'payment_token': self.payment_token_id.display_name})
                reminder_mail_template.with_context(email_context).send_mail(self.id)
                _logger.debug("Sending Payment Failure Mail to %s for contract %s and setting contract to pending", self.partner_id.email, self.id)
                msg_body = 'Automatic payment failed. Contract set to "To Renew". Email sent to customer. Error: %s' % (
                        transaction and transaction.state_message or 'No Payment Method')
            self.message_post(body=msg_body)
            subscription_values = {'to_renew': True, 'payment_exception': False, 'is_batch': True}
        subscription_values.update(self._update_subscription_payment_failure_values())
        self.write(subscription_values)
