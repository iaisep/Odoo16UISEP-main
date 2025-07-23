from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class DocumentFolders(models.Model):
    _name = 'portal.documents.folders'
    _description = 'Directory'
    _order = 'name'
    
    name = fields.Char(string='Name', required=True )
    image = fields.Binary(string="Image")
    
    sequence = fields.Integer('Sequence', default=10)   
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company)
    
    attachment_ids = fields.One2many('ir.attachment', 'folder_id', string="Attachments")
    model_id = fields.Many2one('ir.model', string='Model' )
    attachment_count = fields.Integer(compute="_compute_attachment_count")
    
   
    def name_get(self):
        if not self.env.context.get('hierarchical_naming', True):
            return [(record.id, record.name) for record in self]
        return super(DocumentFolders, self).name_get()

    @api.model
    def name_create(self, name):
        return self.create({'name': name}).name_get()[0]


            
    @api.depends()
    def _compute_attachment_count(self):
        read_group_var = self.env['ir.attachment'].read_group(
            [('folder_id', 'in', self.ids)],
            fields=['folder_id'],
            groupby=['folder_id'])

        attachment_count_dict = dict((d['folder_id'][0], d['folder_id_count']) for d in read_group_var)
        for record in self:
            record.attachment_count = attachment_count_dict.get(record.id, 0)
       
    @api.constrains('model_id')
    def _check_model(self):
        self.ensure_one()
        model = self.env['portal.documents.folders'].sudo().search([('model_id.model', '=', self.model_id.model)])
        if len(model) > 1:
            raise ValidationError(_('This models directory has already been established.!'))
            
    def action_see_attachments(self):
        domain = [('folder_id', '=', self.id)]
        return {
            'name': _('Documents'),
            'domain': domain,
            'res_model': 'ir.attachment',
            'type': 'ir.actions.act_window',
            'views': [(False, 'list'), (False, 'form')],
            'view_mode': 'tree,form',
            'context': "{'default_folder_id': %s}" % self.id
        }

    @api.model
    def create(self,vals):
        result = super(DocumentFolders, self).create(vals)        
        attachments = self.env['ir.attachment'].sudo().search([])
        model_id = vals.get('model_id' ,False)
        if model_id:
            for attachment in attachments:
                model = self.env['ir.model'].sudo().search([('id', '=', model_id)], limit=1)            
                if model and attachment.res_model == model.model:
                    attachment.sudo().write({
                        'folder_id': result.id
                    })
        return result
    