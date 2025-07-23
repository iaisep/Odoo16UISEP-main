# from odoo.addons.openeducat_multi_approval.tests.common import TestSaleCommonBase
from odoo import fields

from odoo.addons.openeducat_multi_approval.tests.common import TestsCommon


class TestMultiApprovalType(TestsCommon):
    def test_multi_approval_type_configure(self):
        x = self.env['multi.approval.type'].search(
            [('id', '=', self.model_approval_type.id)])
        x.action_configure()
        sale_order = self.env['sale.order'].search(
            [('x_is_request', '=', True)], limit=1)
        request_wizard = self.env['multi.model.request'].with_context({
            'active_id': [sale_order.id], 'active_model': 'sale.order'}).create(
            {'name': 'Request approval for S00002',
             'approval_type_id': self.model_approval_type.id,
             'source_document': '%s,%s' % ('sale.order', sale_order.id),
             'description': "Hi, Please review my request. Click <a target='__blank__'"
                            " href=#id=%s&view_type=form&model=%s>%s</a> to view more !"
                            " Thanks," % (sale_order.id, 'sale.order', 'S00002')})
        request_wizard.with_context(
            {'active_id': sale_order.id, 'active_model': 'sale.order',
             'cuu': [sale_order.id]}).action_request()
        vv = self.env['multi.request'].search([])
        vv.action_approve()
        vv.action_refuse()
        vv.action_cancel()
        vv.action_draft()

    def test_normal_approval_type_configure(self):
        x = self.env['multi.approval.type'].search(
            [('id', '=', self.normal_approval_type.id)])
        vv = self.env['multi.request'].create({
            'name': x.name,
            'approval_type_id': x.id,
            'date': fields.Datetime.now(),
            'user_id': self.env.ref('base.user_admin').id,
            'amount': 500,
            'partner_id': self.partner_a.id,
            'line_ids': [(5, 0, 0),
                         (0, 0, {
                          'user_id': self.env.user.id,
                          'require_opt': 'required', })]})
        vv.action_approve()
        vv.action_refuse()
        vv.action_cancel()
        vv.action_draft()
