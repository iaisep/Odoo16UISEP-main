import ast

from lxml import etree

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MultiApproval(models.Model):
    _name = 'multi.approval.type'
    _description = 'MultiApproval'

    name = fields.Char(string='Name')
    image = fields.Image(string="Image")
    description = fields.Char(string='Description')
    priority = fields.Integer(string='Priority')
    apply_for_model = fields.Boolean(string='Apply For Model ?')

    document_opt = fields.Selection([
        ('required', 'Required'),
        ('optional', 'Optional'),
    ], string='Document', default='optional')
    partner_opt = fields.Selection([
        ('required', 'Required'),
        ('optional', 'Optional'),
        ('none', 'None'),
    ], string='Contact', default='none')
    date_opt = fields.Selection([
        ('required', 'Required'),
        ('optional', 'Optional'),
        ('none', 'None'),
    ], string='Date', default='none')
    period_opt = fields.Selection([
        ('required', 'Required'),
        ('optional', 'Optional'),
        ('none', 'None'),
    ], string='Period', default='none')
    product_opt = fields.Selection([
        ('required', 'Required'),
        ('optional', 'Optional'),
        ('none', 'None'),
    ], string='Product', default='none')
    quantity_opt = fields.Selection([
        ('required', 'Required'),
        ('optional', 'Optional'),
        ('none', 'None'),
    ], string='Quantity', default='none')
    amount_opt = fields.Selection([
        ('required', 'Required'),
        ('optional', 'Optional'),
        ('none', 'None'),
    ], string='Amount', default='none')
    payment_opt = fields.Selection([
        ('required', 'Required'),
        ('optional', 'Optional'),
        ('none', 'None'),
    ], string='Payment', default='none')
    reference_opt = fields.Selection([
        ('required', 'Required'),
        ('optional', 'Optional'),
        ('none', 'None'),
    ], string='Reference', default='none')
    location_opt = fields.Selection([
        ('required', 'Required'),
        ('optional', 'Optional'),
        ('none', 'None'),
    ], string='Location', default='none')

    approval_minimum = fields.Integer(string='Minimum Approvers',
                                      compute='_compute_approval_minimum')
    line_ids = fields.One2many(comodel_name='multi.approval.type.line',
                               inverse_name='line', string='Approvers')
    model_name = fields.Char()
    model_id = fields.Many2one(comodel_name='ir.model', string='Model')
    domain = fields.Text(string='Domain')
    hide_button = fields.Boolean(string='Hide Buttons from Model View?', default=False)
    approve_python_code = fields.Text(string='Approved Action')
    refuse_python_code = fields.Text(string='Refused Action')
    is_configured = fields.Boolean(string='Configured')
    active = fields.Boolean(string='Active', default=True)
    is_request = fields.Boolean(string="Request")
    request_to_validate_count = fields.Integer(string="record count",
                                               compute='_compute_to_review_number')

    @api.depends('line_ids.require_opt')
    def _compute_approval_minimum(self):
        self.approval_minimum = 0
        for rec in self.line_ids:
            if rec.require_opt == 'required':
                self.approval_minimum += 1

    def _compute_to_review_number(self):
        for rec in self:
            rec.request_to_validate_count = self.env['multi.request'].search_count(
                [('approval_type_id', '=', rec.name),
                 ('line_ids.user_id', '=', self._uid),
                 ('request_status', '=', 'pending')])

    def create_request(self):
        template_id = self.env['ir.model.data']. \
            _xmlid_to_res_id('openeducat_multi_approval.view_from_approval_request',
                             raise_if_not_found=False)
        return {
            'name': _('Approval Request'),
            'res_model': 'multi.request',
            'view_mode': 'form',
            'views': [(template_id, 'form')],
            'context': {
                'default_approval_type_id': self.id,
                'default_document_opt': self.document_opt,
                'default_partner_opt': self.partner_opt,
                'default_date_opt': self.date_opt,
                'default_period_opt': self.period_opt,
                'default_product_opt': self.product_opt,
                'default_quantity_opt': self.quantity_opt,
                'default_amount_opt': self.amount_opt,
                'default_payment_opt': self.payment_opt,
                'default_reference_opt': self.reference_opt,
                'default_location_opt': self.location_opt,
                'default_line_ids': [(0, 0, {
                    'user_id': rec.user_id.id,
                    'require_opt': rec.require_opt,
                    'approve_tmpl_id':
                        rec.approve_tmpl_id and rec.approve_tmpl_id.id or False,
                    'reject_tmpl_id':
                        rec.reject_tmpl_id and rec.reject_tmpl_id.id or False
                }) for rec in self.line_ids]
            },
            'target': 'current',
            'type': 'ir.actions.act_window',
        }

    @api.onchange('model_id')
    def onchange_model_id(self):
        self.model_name = str(self.model_id.model)

    @api.constrains('line_ids')
    def _constrains_approval_minimum(self):
        if self.approval_minimum < 1:
            raise ValidationError(_('You have to add at least 1 approvers to Approval'
                                    ' Type.'))

    def action_configure(self, view_id=None, view_type='form',
                         toolbar=False, submenu=False):
        self.is_configured = True
        x = self.env['ir.ui.view'].search(
            [('model', '=', self.model_name), ('inherit_id', '=', False),
             ('type', '=', 'form')])
        inherit_id = self.env.ref(x.xml_id)
        p = self.env['ir.actions.act_window'].search(
            [('name', '=', 'Approval Model Request')])
        v = self.env['ir.actions.server'].search(
            [('name', '=', 'View Approval Request')])
        f = self.env['ir.model.fields'].search([('name', '=', 'x_is_request'),
                                                ('model_id', '=', self.model_id.id)])

        if not f:
            self.env['ir.model.fields'].sudo().create(
                [({'name': 'x_is_request',
                   'field_description': 'Is Request',
                   'ttype': 'boolean',
                   'model_id': self.model_id.id}),
                 ({'name': 'x_is_view_approval',
                   'field_description': 'Is View Approval',
                   'ttype': 'boolean',
                   'model_id': self.model_id.id}),
                 ({'name': 'x_result_approval',
                   'field_description': 'Result Approval',
                   'ttype': 'selection',
                   'selection_ids': [(0, 0, {'value': 'approve',
                                             'name': 'Approve'}),
                                     (0, 0, {'value': 'refuse',
                                             'name': 'Refuse'})],
                   'model_id': self.model_id.id}),
                 ({'name': 'x_is_hide',
                   'field_description': 'Is Hide',
                   'ttype': 'boolean',
                   'model_id': self.model_id.id})])
        self.env['ir.model.fields'].search([('name', '=', 'x_is_hide'),
                                            ('model_id', '=', self.model_id.id)])
        b = {'invisible': ['|', ('x_is_request', '=', False),
                           ('x_is_view_approval', '=', True)]}
        va = {'invisible': [('x_is_view_approval', '=', False)]}
        na = {'invisible': ['|', ('x_is_request', '=', False),
                            ('x_result_approval', '!=', False)]}
        ha = {'invisible': ['|', ('x_result_approval', '!=', 'approve'),
                            ('x_is_request', '=', False)]}
        ra = {'invisible': ['|', ('x_result_approval', '!=', 'refuse'),
                            ('x_is_request', '=', False)]}
        do = self.env[self.model_name].search(ast.literal_eval(self.domain))
        for recs in do:
            recs.x_is_request = True
            if self.hide_button:
                recs.x_is_hide = True
        arch_base = _('<?xml version="1.0"?>'
                      '<data>'
                      '<field name="state" position="after">'
                      '<field name="x_is_request" invisible="1"/>'
                      '<field name="x_is_view_approval" invisible="1"/>'
                      '<field name="x_result_approval" invisible="1"/>'
                      '<field name="x_is_hide" invisible="1"/>'
                      '<button name="%s" string="Create New Request" type="action"'
                      ' class="btn-primary" attrs="%s"/>'
                      '<button name="%s" string="View Approval" type="action"'
                      ' class="btn-primary" attrs="%s"/>'
                      '</field>'
                      '<xpath expr="//form/header" position="after">'
                      '<div>'
                      '<div attrs="%s" class="alert alert-warning"'
                      ' style="margin-bottom:0px;" role="alert">'
                      'This document need to be approved !'
                      '</div>'
                      '<div attrs="%s" class="alert alert-info"'
                      ' style="margin-bottom:0px;" role="alert">'
                      'This document has been approved !'
                      '</div>'
                      '<div attrs="%s" class="alert alert-danger"'
                      ' style="margin-bottom:0px;" role="alert">'
                      'This document has been refused !'
                      '</div>'
                      '</div>'
                      '</xpath>'
                      '</data>') % (p.id, b, v.id, va, na, ha, ra)
        if not f:
            self.env['ir.ui.view'].sudo().create({'name': '%s' % self.model_name,
                                                  'type': 'form',
                                                  'model': '%s' % self.model_name,
                                                  'mode': 'extension',
                                                  'inherit_id': inherit_id.id,
                                                  'arch_base': arch_base,
                                                  'active': True})
        if not f:
            if view_type == 'form':
                doc = etree.XML(x['arch'])
                for node in doc.xpath("//header/button"):
                    m = node.get('attrs')
                    if not m:
                        ml = node.get('states')
                        if ml:
                            node.set("attrs", "{'invisible':['|',"
                                              "('x_is_hide', '=', True),"
                                              "('state','not in',"
                                     + str(ml.split(',')) + ")]}")
                            node.set("states", " ")
                    if m:
                        bb = m[m.find("|"):m.rfind("}")]
                        dd = "('x_is_hide', '=', True),"
                        bb = dd + "'" + bb
                        node.set("attrs", "{'invisible':['|'," + bb + "}")
                        if bb.count("|") == 0:
                            bb = m[m.find("("):m.rfind("}")]
                            bb = dd + bb
                            node.set("attrs", "{'invisible':['|'," + bb + "}")
                x['arch'] = etree.tostring(doc, encoding='unicode')
        if self.hide_button:
            self.env['base.automation'].create({
                'name': self.name + " Action",
                'model_id': self.model_id.id,
                'active': True,
                'state': 'object_write',
                'trigger': 'on_create_or_write',
                'filter_domain': self.domain,
                'fields_lines': [
                    (0, 0, {'col1': self.env['ir.model.fields'].
                     search([('name', '=', 'x_is_request'),
                             ('model_id', '=', self.model_id.id)]).id,
                            'evaluation_type': 'value', 'value': True}),
                    (0, 0, {'col1': self.env['ir.model.fields'].
                     search([('name', '=', 'x_is_hide'),
                             ('model_id', '=', self.model_id.id)]).id,
                            'evaluation_type': 'value', 'value': self.hide_button})]
            })
        else:
            self.env['base.automation'].create({
                'name': self.name + " Action",
                'model_id': self.model_id.id,
                'active': True,
                'state': 'object_write',
                'trigger': 'on_create_or_write',
                'filter_domain': self.domain,
                'fields_lines': [
                    (0, 0, {'col1': self.env['ir.model.fields'].
                     search([('name', '=', 'x_is_request'),
                             ('model_id', '=', self.model_id.id)]).id,
                            'evaluation_type': 'value', 'value': True})]
            })

    def unlink(self):
        auto_action = self.env['base.automation'].search(
            [('name', '=', self.name + " Action")])
        auto_action.unlink()
        request_record = self.env['multi.request'].search(
            [('approval_type_id', '=', self.id)])
        request_record.unlink()
        record = self.env[self.model_name].search(ast.literal_eval(self.domain))
        for rec in record:
            rec.x_is_request = False
            rec.x_is_hide = False
            rec.x_is_view_approval = False
        return super().unlink()


class MultiApprovalLine(models.Model):
    _name = 'multi.approval.type.line'
    _description = 'MultiApprovalLine'

    line = fields.Many2one(comodel_name='multi.approval.type',
                           string='MultiApprovalLine')
    user_id = fields.Many2one(comodel_name='res.users', string='User')
    require_opt = fields.Selection([
        ('required', 'Required'),
        ('optional', 'Optional'),
    ], string='Type of Approval', default='optional')
    approve_tmpl_id = fields.Many2one('mail.template', string="Approve Template")
    reject_tmpl_id = fields.Many2one('mail.template', string="Reject Template")
