# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class CertificateLog(models.Model):
    _name = "certificate.log"
    _description = "Certificate Log"
    _order = 'date desc'

    download_from = fields.Selection([('web','Sitio Web'),('internal','Interno')], string="Ruta de Descarga", default='internal', readonly=True)
    certificate_name = fields.Char(string="Certificado", readonly=True)
    invoice_id = fields.Many2one('account.move', string="Factura", readonly=True)
    student_id = fields.Many2one('op.student', string="Estudiante", readonly=True)
    user_id = fields.Many2one('res.users', string="Usuario", readonly=True)
    date = fields.Datetime(string='Download Date', readonly=True)

    
