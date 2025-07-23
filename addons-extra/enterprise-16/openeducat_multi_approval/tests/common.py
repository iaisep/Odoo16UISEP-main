# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.tests import common


class TestsCommon(common.TransactionCase):

    def setUp(self):
        super(TestsCommon, self).setUp()
        self.normal_approval_type = self.env['multi.approval.type'].create({
            'name': 'XYZ Test',
            'description': 'XYZ Amount Approval Test',
            'amount_opt': 'required',
            'partner_opt': 'required',
            'line_ids': [(5, 0, 0),
                         (0, 0, {
                             'user_id': self.env.user.id,
                             'require_opt': 'required'})],
        })
        self.model_approval_type = self.env['multi.approval.type'].create({
            'name': 'Sale Test',
            'description': 'Sale Approval Test',
            'apply_for_model': True,
            'model_id': self.env.ref('sale.model_sale_order').id,
            'model_name': 'sale.order',
            'domain': "[['state','=','draft'],['amount_total','>',1000]]",
            'hide_button': True,
            'approve_python_code': 'record.action_confirm',
            'refuse_python_code': 'record.action_cancel',
            'line_ids': [(5, 0, 0),
                         (0, 0, {
                             'user_id': self.env.user.id,
                             'require_opt': 'required', })
                         ],
        })
        self.env['ir.model.fields'].sudo().create([({
            'name': 'x_is_request',
            'field_description': 'Is Request',
            'ttype': 'boolean',
            'model_id': self.env.ref('sale.model_sale_order').id}),
            ({'name': 'x_is_view_approval',
              'field_description': 'Is View Approval',
              'ttype': 'boolean',
              'model_id': self.env.ref('sale.model_sale_order').id}),
            ({'name': 'x_result_approval',
              'field_description': 'Result Approval',
              'ttype': 'selection',
              'selection_ids': [(0, 0, {'value': 'approve',
                                        'name': 'Approve'}),
                                (0, 0, {'value': 'refuse',
                                        'name': 'Refuse'}), ],
             'model_id': self.env.ref('sale.model_sale_order').id}),
            ({'name': 'x_is_hide',
              'field_description': 'Is Hide',
              'ttype': 'boolean',
              'model_id': self.env.ref('sale.model_sale_order').id})])
        self.partner_a = self.env['res.partner'].create({
            'name': 'Test Partner',
            'company_id': False,
        })
