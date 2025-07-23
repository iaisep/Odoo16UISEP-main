# -*- coding: utf-8 -*-

from odoo import models, fields

class ResCompany(models.Model):
    _inherit = "res.company"

    cert_product_id = fields.Many2one('product.product', string="Product para Facturar Certificados", help="Producto usado para generar la factura a pagar por el certificado solicitado por el estudiante")

    op_sign_certificate_ids = fields.Many2many('op.sign_certificate',
        string='Sign Certificates')


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    cert_product_id = fields.Many2one('product.product', string="Product para Facturar Certificados", related="company_id.cert_product_id", readonly= False, help="Producto usado para generar la factura a pagar por el certificado solicitado por el estudiante")
    cert_days_fpayment = fields.Char(string="Horas de gracia para pagar certificado", config_parameter="cert_days_fpayment")
    cert_days_fdownload = fields.Char(string="Horas de gracia para descargar certificado", config_parameter="cert_days_fdownload")

    op_sign_certificate_ids = fields.Many2many(
        related='company_id.op_sign_certificate_ids', readonly=False,
        string='Op Sign Certificates')




