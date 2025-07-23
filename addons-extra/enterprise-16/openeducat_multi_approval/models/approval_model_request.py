import ast

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ApprovalModelRequest(models.Model):
    _name = 'multi.model.request'
    _description = 'ApprovalModelRequest'

    name = fields.Char()
    priority = fields.Integer(string='Priority')
    request_date = fields.Datetime(string='Requested Date',
                                   default=fields.Datetime.now)
    approval_type_id = fields.Many2one(comodel_name='multi.approval.type',
                                       string='Approval Type')
    description = fields.Html(string='Description')
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user)

    @api.model
    def _select_target_model(self):
        active_model = self.env.context.get('active_model')
        models = self.env['ir.model'].search([('model', '=', active_model)])
        return [(model.model, model.name) for model in models]

    source_document = fields.Reference(selection='_select_target_model',
                                       string="Source Document")

    @api.model
    def default_get(self, fields_list):
        active_id = self.env.context.get('active_id')
        active_model = self.env.context.get('active_model')
        cuu = self.env[active_model].search([('id', '=', active_id)])
        x = self.env['multi.approval.type'].search(
            [('model_name', '=', active_model)])
        for rec in x:
            p = ast.literal_eval(rec.domain)
            v = self.env[active_model].search(p)
            if cuu in v:
                type_id = self.env['multi.approval.type'].search(
                    [('name', '=', rec.name)])
        res = super(ApprovalModelRequest, self).default_get(fields_list)

        web_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        action_id = self.env.ref('sale.action_quotations_with_onboarding',
                                 raise_if_not_found=False)
        link = """{}/web#id={}&view_type=form&model={}&action={}""".format(web_base_url,
                                                                           active_id,
                                                                           active_model,
                                                                           action_id.id)

        html_links = 'Hi, <br/><br/> Please review my request.' \
                     'Click <a href="%s" target="_blank">%s</a> ' \
                     'to view more ! <br/> <br/>Thanks,' % (link, cuu.display_name)
        res.update({
            'name': f"Request approval for {cuu.display_name}",
            'approval_type_id': type_id,
            'source_document': '%s,%s' % (active_model, active_id),
            'description': html_links
        })
        return res

    def send_multiapprove_mail(self, cuu):
        self.env['mail.mail']
        email_list = ''
        self.env.context.get('active_id')
        self.env.context.get('active_model')
        if self.approval_type_id:
            for line in self.approval_type_id.line_ids:
                if line.user_id.email:
                    email_list += ',' + str(line.user_id.email)
                else:
                    raise UserError(_('Please Configure Your Email %s .',
                                      line.user_id.name))

        email_from = self.env.user.partner_id.email
        if not email_from:
            raise UserError(_('Please Configure Sender Email',
                              self.env.user.partner_id.name))
        template_data = {
            'subject': 'Multi Approve',
            'body_html': self.description,
            'email_from': email_from,
            'email_to': email_list
        }
        template_id = self.env.ref(
            'openeducat_multi_approval.email_template_multi_approve_from_sale',
            raise_if_not_found=False)
        if template_id:
            template_id.sudo().send_mail(self.id, force_send=True,
                                         email_values=template_data)

    def action_request(self):
        active_id = self.env.context.get('active_id')
        active_model = self.env.context.get('active_model')
        cuu = self.env[active_model].search([('id', '=', active_id)])
        cuu.x_is_view_approval = True

        self.env['multi.request'].create({
            'name': self.name if self.name else None,
            'approval_type_id': self.approval_type_id.id,
            'date': fields.Datetime.now(),
            'reason': self.description,
            'reference': cuu.display_name if cuu.display_name else None,
            'request_status': 'pending',
            'source_document': '%s,%s' % (active_model, active_id),
            'line_ids': [(0, 0, {'user_id': rec.user_id.id,
                                 'require_opt': rec.require_opt,
                                 'approve_tmpl_id':
                                     rec.approve_tmpl_id and
                                     rec.approve_tmpl_id.id or False,
                                 'reject_tmpl_id':
                                     rec.reject_tmpl_id and
                                     rec.reject_tmpl_id.id or False,

                                 }) for rec in self.approval_type_id.line_ids]
        })
        self.send_multiapprove_mail(cuu)
