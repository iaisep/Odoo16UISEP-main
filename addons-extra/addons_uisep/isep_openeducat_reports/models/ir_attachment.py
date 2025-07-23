# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import timedelta
import logging

_logger = logging.getLogger(__name__)

class IrAttachment(models.Model):
    _inherit = ['ir.attachment']
    _name = 'ir.attachment'

    sign_certificate_id = fields.Many2one('account.move', string="Sign Certificate")
    cert_invoice_id = fields.Many2one('account.move', string="Factura del Certificado")
    certificado_web = fields.Boolean(string="Certificado Web")
    certificado_gratuito = fields.Boolean(string="Certificado Gratuito")
    cert_invoice_done = fields.Boolean(string="No necesita revision")


    
    def _cron_cleanup_certificado_web_attachments(self):
        cert_days_fpayment = int(self.env["ir.config_parameter"].sudo().get_param("cert_days_fpayment")) or 5
        attachments_to_check = self.env['ir.attachment'].search([
            ('cert_invoice_done','=', False),
            ('cert_invoice_id', '!=', False),
            ('certificado_web','=',True)
        ])
        _logger.info('\n##############\n##############'+str(attachments_to_check))

        for attachment in attachments_to_check:
            invoice = attachment.cert_invoice_id

            if invoice.payment_state == 'not_paid':
                
                date_limit = fields.Date.today() - timedelta(days=cert_days_fpayment)   
                _logger.info('\n##############\n##############'+str(invoice.invoice_date)+'\n##############'+str(date_limit))
                if invoice.invoice_date <= date_limit and invoice.payment_state in ['not_paid']:
                    try:
                        if invoice.state != 'draft':
                            invoice.sudo().button_draft()
                        invoice.unlink()
                        attachment.unlink()

                        self._cr.commit()

                    except Exception as e:
                        self._cr.rollback()
            else:
                attachment.cert_invoice_done = True
                self._cr.commit()
        
        cert_days_fdownload = int(self.env["ir.config_parameter"].sudo().get_param("cert_days_fdownload")) or 30
        date_limit = fields.Date.today() - timedelta(days=cert_days_fdownload)
        attachments_to_check_free = self.env['ir.attachment'].search([
            ('certificado_web','=',True),
            ('certificado_gratuito','=',True),
            ('create_date', '<=', date_limit)  
        ])

        attachments_to_check_free.unlink()
        


    def validate_access(self, access_token):
        # Check if is certificate
        if self.sudo().certificado_web:
            # Check if student and user 
            student_id = self.env['op.student'].sudo().search([('user_id','=',self.env.user.id)], limit=1)
            if self.env.is_superuser() or (self.sudo().res_id == student_id.id and self.sudo().res_model == 'op.student'):
                if self.sudo().certificado_gratuito:
                    return self.sudo()
                if self.sudo().cert_invoice_id and self.sudo().cert_invoice_id.payment_state == 'paid':
                    return self.sudo()
            
        res = super().validate_access(access_token)
        return res

    # Funcion no optimizada 
    def remove_certificates(self):
       
        try:
           cert_days_fpayment = int(self.env["ir.config_parameter"].sudo().get_param("cert_days_fpayment"))
        except ValueError:
           cert_days_fpayment = 7
        try:
           cert_days_fdownload = int(self.env["ir.config_parameter"].sudo().get_param("cert_days_fdownload"))
        except ValueError:
           cert_days_fdownload = 3

        certificados = self.search([('certificado_web','=',True)])
        certificados_vencidos_cfactura = certificados.filtered(lambda c: c.cert_invoice_id and c.cert_invoice_id.payment_state != 'paid' and ((c.create_date + timedelta(days=cert_days_fpayment))  < fields.Datetime.now()))
        certificados_vencidos_cfactura.unlink()

        certificados = self.search([('certificado_web','=',True)])
        certificados_vencidos_pagados = certificados.filtered(lambda c: c.cert_invoice_id and c.cert_invoice_id.payment_state == 'paid' and ((c.cert_invoice_id.get_last_payment_date() + timedelta(days=cert_days_fdownload))  < fields.Date.today()))
        certificados_vencidos_pagados.unlink()

        certificados = self.search([('certificado_web','=',True),('certificado_gratuito','=',True)])
        certificados_vencidos_gratuitos = certificados.filtered(lambda c: (c.create_date + timedelta(days=cert_days_fpayment))  < fields.Datetime.now())
        certificados_vencidos_gratuitos.unlink()

        return
