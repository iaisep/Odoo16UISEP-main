# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from collections import OrderedDict

from odoo import _, http
from odoo.exceptions import AccessError, MissingError
from odoo.http import request

from odoo.addons.account.controllers.portal import PortalAccount
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager


class CustomerPortalInvoice(CustomerPortal):
    def _parent_prepare_portal_layout_values(self, student_id=None):
        val = super(CustomerPortalInvoice, self)\
            ._parent_prepare_portal_layout_values(student_id)
        student = request.env['op.student'].sudo().search([('id', '=', student_id)])

        invoice_count = request.env['account.move'].sudo().search_count([
            ('partner_id', '=', student.partner_id.id), ('state', 'not in', ['draft']),
            ('move_type', 'in',
             ('out_invoice', 'in_invoice',
              'out_refund', 'in_refund',
              'out_receipt', 'in_receipt'))]
        ) if request.env['account.move']\
            .check_access_rights('read', raise_exception=False) else 0

        val['invoice_count'] = invoice_count
        return val

    def _prepare_portal_layout_values(self):
        values = super(PortalCoreAccount, self)._prepare_portal_layout_values()

        invoice_count = request.env['account.move'].search_count([
            ('partner_id', '=', request.env.user.partner_id.id),
            ('move_type', 'in',
             ('out_invoice', 'in_invoice',
              'out_refund', 'in_refund',
              'out_receipt', 'in_receipt'))]
        ) if request.env['account.move'].check_access_rights(
            'read', raise_exception=False) else 0
        values['invoice_count'] = invoice_count
        return values


class PortalCoreAccount(PortalAccount):

    @http.route(['/my/invoices/',
                 '/my/invoice/<int:student_id>',
                 '/my/invoices/page/<int:page>'],
                type='http', auth="user", website=True)
    def portal_core_invoices(self, page=1, date_begin=None, date_end=None,
                             sortby=None, filterby=None, student_id=None, **kw):
        if student_id:
            val = self._parent_prepare_portal_layout_values(student_id)
        else:
            values = self._prepare_portal_layout_values()
        AccountInvoice = request.env['account.move']

        domain = [
            ('state', 'not in', ['draft']), ('move_type', 'in',
                                             ('out_invoice', 'out_refund',
                                              'in_invoice', 'in_refund',
                                              'out_receipt', 'in_receipt'))]

        searchbar_sortings = {
            'date': {'label': _('Date'), 'order': 'invoice_date desc'},
            'duedate': {'label': _('Due Date'), 'order': 'invoice_date_due desc'},
            'name': {'label': _('Reference'), 'order': 'name desc'},
            'state': {'label': _('Status'), 'order': 'state'},
        }
        # default sort by order
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'invoices': {'label': _('Invoices'),
                         'domain': [('move_type', '=', ('out_invoice', 'out_refund'))]},
            'bills': {'label': _('Bills'),
                      'domain': [('move_type', '=', ('in_invoice', 'in_refund'))]},
        }
        # default filter by value
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin),
                       ('create_date', '<=', date_end)]

        # count for pager
        invoice_count = AccountInvoice.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/invoices",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=invoice_count,
            page=page,
            step=self._items_per_page
        )
        if student_id:
            student = request.env['op.student'].sudo().search([('id', '=', student_id)])
            domain += [('partner_id', '=', student.partner_id.id)]
            parent_invoices = AccountInvoice.sudo().search(domain, order=order,
                                                           limit=self._items_per_page,
                                                           offset=pager['offset'])
            request.session['my_invoices_history'] = parent_invoices.ids[:100]
        else:
            domain += [('partner_id', '=', request.env.user.partner_id.id)]
            invoices = AccountInvoice.sudo().search(domain, order=order,
                                                    limit=self._items_per_page,
                                                    offset=pager['offset'])
            request.session['my_invoices_history'] = invoices.ids[:100]
        # content according to pager and archive selected

        if student_id:
            val.update({
                'date': date_begin,
                'invoices': parent_invoices,
                'page_name': 'invoice',
                'std_id': student_id,
                'pager': pager,
                'default_url': '/my/invoices/%s' % student_id,
                'searchbar_sortings': searchbar_sortings,
                'sortby': sortby,
                'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
                'filterby': filterby,
            })
            return request.render("account.portal_my_invoices", val)

        else:
            values.update({
                'date': date_begin,
                'invoices': invoices,
                'page_name': 'invoice',
                'pager': pager,
                'default_url': '/my/invoices',
                'searchbar_sortings': searchbar_sortings,
                'sortby': sortby,
                'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
                'filterby': filterby,
            })
            return request.render("account.portal_my_invoices", values)

    @http.route(['/my/invoices/<int:student_id>'],
                type='http', auth="public", website=True)
    def portal_core_invoice_detail(self, invoice_id=None, access_token=None,
                                   report_type=None, download=False,
                                   student_id=None, **kw):
        if student_id:
            try:
                invoice_sudo = self._document_check_access(
                    'account.move', student_id, access_token)
            except (AccessError, MissingError):
                return request.redirect('/my/invoice/%s' % (student_id))

            if report_type in ('html', 'pdf', 'text'):
                return self._show_report(model=invoice_sudo, report_type=report_type,
                                         report_ref='account.account_invoices',
                                         download=download)

            values = self._invoice_get_page_view_values(
                invoice_sudo, access_token, **kw)
            acquirers = values.get('acquirers')
            if acquirers:
                country_id = values.get('partner_id') and values.get(
                    'partner_id')
                values['acq_extra_fees'] = acquirers._compute_fees(
                    invoice_sudo.amount_residual, invoice_sudo.currency_id, country_id)

            return request.render("account.portal_invoice_page", values)
