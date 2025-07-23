# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class SepReportLog(models.Model):
    _name = "sep.report.log"
    _description = "Sep Report Log"
    _order = 'date desc'
    
    date = fields.Datetime(string='Fecha de Descarga', readonly=True)
    user_id = fields.Many2one('res.users', string="Usuario", readonly=True)
    annex = fields.Selection([('8','Anexo 8'),('9','Anexo 9')], string="Anexo", readonly=True)
    attachment_id = fields.Many2one('ir.attachment', string="Archivo Descargado", readonly=True)
   

    def action_download_attachment(self):
        self.ensure_one()
        if not self.attachment_id:
            raise UserError(_('No attachment found'))
        return {
            'type': 'ir.actions.act_url',
            'url': self.get_base_url() + '/web/content/%s?download=true' % self.attachment_id.id,
            'target': 'new',
        }    
