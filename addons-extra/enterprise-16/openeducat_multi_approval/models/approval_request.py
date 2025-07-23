from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval


class ApprovalRequest(models.Model):
    _name = 'multi.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Approval Request'
    _order = 'id desc'

    name = fields.Char(string='Name')
    user_id = fields.Many2one(comodel_name='res.users', string='Request by',
                              default=lambda self: self._uid)
    approval_type_id = fields.Many2one(comodel_name='multi.approval.type',
                                       string='Approval Type')
    date_confirmed = fields.Datetime(string='Date Confirm')
    date = fields.Datetime(string='Request Date')
    date_start = fields.Datetime(string='Date End')
    date_end = fields.Datetime(string='Date Start')
    location = fields.Char(string='Location')
    partner_id = fields.Many2one(comodel_name='res.partner', string='Contact')
    quantity = fields.Integer(string='Quantity')
    amount = fields.Float(string='Amount')
    reference = fields.Char(string='Reference')
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)
    request_status = fields.Selection([
        ('new', 'To Submit'),
        ('pending', 'Submitted'),
        ('approved', 'Approved'),
        ('refused', 'Refused'),
        ('cancel', 'Cancel'),
    ], default='new')
    user_status = fields.Selection([
        ('new', 'To Submit'),
        ('pending', 'Submitted'),
        ('approved', 'Approved'),
        ('refused', 'Refused'),
        ('cancel', 'Cancel'),
    ], string='User Status', default='new')
    line_ids = fields.One2many(comodel_name='multi.request.line',
                               inverse_name='line', string='Approvers')
    product_line_ids = fields.One2many(comodel_name='multi.product.line',
                                       inverse_name='line_product', string='Products')
    reason = fields.Html(string='Description')
    document_opt = fields.Selection([
        ('required', 'Required'),
        ('optional', 'Optional'),
    ], default='optional')
    partner_opt = fields.Selection([
        ('required', 'Required'),
        ('optional', 'Optional'),
        ('none', 'None'),
    ], default='none')
    date_opt = fields.Selection([
        ('required', 'Required'),
        ('optional', 'Optional'),
        ('none', 'None'),
    ])
    period_opt = fields.Selection([
        ('required', 'Required'),
        ('optional', 'Optional'),
        ('none', 'None'),
    ], default='none')
    product_opt = fields.Selection([
        ('required', 'Required'),
        ('optional', 'Optional'),
        ('none', 'None'),
    ], default='none')
    quantity_opt = fields.Selection([
        ('required', 'Required'),
        ('optional', 'Optional'),
        ('none', 'None'),
    ], default='none')
    amount_opt = fields.Selection([
        ('required', 'Required'),
        ('optional', 'Optional'),
        ('none', 'None'),
    ], default='none')
    payment_opt = fields.Selection([
        ('required', 'Required'),
        ('optional', 'Optional'),
        ('none', 'None'),
    ], default='none')
    reference_opt = fields.Selection([
        ('required', 'Required'),
        ('optional', 'Optional'),
        ('none', 'None'),
    ], default='none')
    location_opt = fields.Selection([
        ('required', 'Required'),
        ('optional', 'Optional'),
        ('none', 'None'),
    ], default='none')
    attachment_number = fields.Integer('Number of Attachments',
                                       compute='_compute_attachment_number')

    @api.model
    def _select_target_model(self):
        active_model = self.env.context.get('active_model')
        models = self.env['ir.model'].search([('model', '=', active_model)])
        return [(model.model, model.name) for model in models]

    source_document = fields.Reference(selection='_select_target_model',
                                       string="Source Document")

    def _compute_attachment_number(self):
        attachment_data = self.env['ir.attachment'].read_group(
            [('res_model', '=', 'multi.request'), ('res_id', 'in', self.ids)],
            ['res_id'], ['res_id'])
        attachment = {data['res_id']: data['res_id_count']
                      for data in attachment_data}
        for rec in self:
            rec.attachment_number = attachment.get(rec.id, 0)

    def action_get_attachment_view(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window']._for_xml_id('base.action_attachment')
        res['domain'] = [('res_model', '=', 'multi.request'),
                         ('res_id', 'in', self.ids)]
        res['context'] = {'default_res_model': 'multi.request',
                          'default_res_id': self.id}
        return res

    def action_confirm(self):
        for rec in self.line_ids:
            if rec.user_id.id == self.env.user.id:
                rec.status = 'pending'
        self.write({'request_status': 'pending',
                    'date_confirmed': fields.Datetime.now()})

    def send_user_approval_mail(self, rec):
        email_values = {}
        if rec.approve_tmpl_id:
            email_values['email_to'] = self.user_id.email
            rec.approve_tmpl_id.send_mail(self.id, force_send=True,
                                          email_values=email_values)

    def action_approve(self):
        v = self.env['multi.approval.type'].search(
            [('name', '=', self.approval_type_id.name)])
        required_count =\
            [rec.id for rec in self.line_ids if rec.require_opt == 'required']
        for rec in self.line_ids:
            if self.env.user.id not in self.line_ids.user_id.ids:
                raise ValidationError(_('You are not in the user allowed list.'))

            if rec.user_id.id == self.env.user.id and rec.status != 'approved':
                rec.status = 'approved'
                approved_count =\
                    [rec.id for rec in self.line_ids
                     if rec.status == 'approved' and rec.require_opt == 'required']
                self.send_user_approval_mail(rec)
                if v.apply_for_model and len(approved_count) == len(required_count):
                    expr = v.approve_python_code
                    ctx = ({'record': self.source_document,
                            'active_model': v.model_id.model})
                    if expr:
                        safe_eval(expr, ctx, mode='exec', nocopy=True)
                    x = self.env[self.approval_type_id.model_name].search(
                        [('id', '=', self.source_document.id)])
                    x.x_result_approval = 'approve'
                    x.x_is_hide = False
                if len(approved_count) == len(required_count):
                    self.request_status = 'approved'

    def send_user_refuse_mail(self, rec):
        email_values = {}
        if rec.reject_tmpl_id:
            email_values['email_to'] = self.user_id.email
            rec.reject_tmpl_id.send_mail(self.id, force_send=True,
                                         email_values=email_values)

    def action_refuse(self):
        v = self.env['multi.approval.type'].search(
            [('name', '=', self.approval_type_id.name)])
        required_count = [rec.id for rec in self.line_ids
                          if rec.require_opt == 'required']
        for rec in self.line_ids:
            if self.env.user.id not in self.line_ids.user_id.ids:
                raise ValidationError(_('You are not in the user allowed list.'))
            if rec.user_id.id == self.env.user.id and rec.status != 'refused':
                rec.status = 'refused'
                self.send_user_refuse_mail(rec)
                refused_count = \
                    [rec.id for rec in self.line_ids
                     if rec.status == 'refused' and rec.require_opt == 'required']
                if v.apply_for_model and len(refused_count) == len(required_count):
                    x = self.env[self.approval_type_id.model_name].search(
                        [('id', '=', self.source_document.id)])
                    x.x_result_approval = 'refuse'
                    expr = v.refuse_python_code
                    ctx = ({'record': self.source_document,
                            'active_model': v.model_id.model})
                    if expr:
                        safe_eval(expr, ctx, mode='exec', nocopy=True)
                    self.request_status = 'refused'

    def action_draft(self):
        for rec in self.line_ids:
            if rec.user_id.id == self.env.user.id:
                rec.status = 'new'
        self.write({'request_status': 'new'})

    def action_cancel(self):
        required_count = [rec.id for rec in self.line_ids
                          if rec.require_opt == 'required']

        for rec in self.line_ids:
            if rec.user_id.id == self.env.user.id:
                rec.status = 'cancel'
        cancel_count =\
            [rec.id for rec in self.line_ids
             if rec.require_opt == 'required' and rec.status == 'cancel']
        if len(required_count) == len(cancel_count):
            self.write({'request_status': 'cancel'})

    def action_view_approval(self):
        active_id = self.env.context.get('active_id')
        active_model = self.env.context.get('active_model')
        cuu = self.env[active_model].search([('id', '=', active_id)])
        return {
            'name': _('View Approval Request'),
            'domain': [('reference', '=', cuu.display_name)],
            'res_model': 'multi.request',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }


class ApprovalRequestLine(models.Model):
    _name = 'multi.request.line'
    _description = 'ApprovalRequestLine'

    line = fields.Many2one(comodel_name='multi.request', string='ApprovalRequestLine')
    user_id = fields.Many2one(comodel_name='res.users', string='User')
    approval_minimum = fields.Integer()
    require_opt = fields.Selection([
        ('required', 'Required'),
        ('optional', 'Optional'),
    ], string='Type of Approval')
    status = fields.Selection([
        ('new', 'New'),
        ('pending', 'To Approve'),
        ('approved', 'Approved'),
        ('refused', 'Refused'),
        ('cancel', 'Cancel'),
    ], string='Status', default='new')
    approve_tmpl_id = fields.Many2one('mail.template', string="Approve Template")
    reject_tmpl_id = fields.Many2one('mail.template', string="Reject Template")


class ApprovalProductLine(models.Model):
    _name = 'multi.product.line'
    _description = 'ApprovalProductLine'

    line_product = fields.Many2one(comodel_name='multi.request',
                                   string='ApprovalProductLine')
    product_id = fields.Many2one(comodel_name='product.product', string='Product')
    quantity = fields.Integer(string='Quantity', default=1)
    product_uom_id = fields.Many2one(comodel_name='uom.uom', string='Unit Of Measure',
                                     related='product_id.uom_id')
