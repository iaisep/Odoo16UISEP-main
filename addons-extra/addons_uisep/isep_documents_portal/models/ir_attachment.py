from odoo import models, fields, api, _

class IrAttachment(models.Model):
    _name = 'ir.attachment'
    _inherit = ['ir.attachment', 'mail.thread']
    
    folder_id = fields.Many2one('portal.documents.folders', string='Directory')
    

    