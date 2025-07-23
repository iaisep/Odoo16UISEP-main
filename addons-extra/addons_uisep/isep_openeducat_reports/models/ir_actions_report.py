# -*- coding: utf-8 -*-
from io import BytesIO
from PyPDF2 import PdfReader, PdfWriter
import os
import copy
from odoo.modules.module import get_module_path
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    certificado_web = fields.Boolean(string="Certificado Web")
    certificado_gratuito = fields.Boolean(string="Certificado Gratuito")
    list_price = fields.Float(string="Precio del Certificado", digits=(6,0))


    @api.model
    def _run_wkhtmltopdf(
            self,
            bodies,
            report_ref=False,
            header=None,
            footer=None,
            landscape=False,
            specific_paperformat_args=None,
            set_viewport_size=False):
            
            pdf_content = super()._run_wkhtmltopdf(
            bodies,
            report_ref,
            header,
            footer,
            landscape,
            specific_paperformat_args,
            set_viewport_size)

            if report_ref == 'isep_openeducat_reports.t_cert_diploma':
                module_path = get_module_path('isep_openeducat_reports')
                watermark_pdf_path = os.path.join(module_path, 'static/src/img/background.pdf')
                # Add watermark to PDF
                pdf_content = self._add_pdf_watermark(pdf_content, watermark_pdf_path)

            return pdf_content

    def _add_pdf_watermark(self, pdf_bytes, watermark_pdf_path):
        input_pdf = PdfReader(BytesIO(pdf_bytes))
        watermark_pdf = PdfReader(watermark_pdf_path)

        output_pdf = PdfWriter()

        for content_page in input_pdf.pages:
            watermark_page_copy = copy.deepcopy(watermark_pdf.pages[0])
            watermark_page_copy.merge_page(content_page)
            output_pdf.add_page(watermark_page_copy)

        output_stream = BytesIO()
        output_pdf.write(output_stream)
        return output_stream.getvalue()

    @api.constrains('list_price')
    def _check_list_price(self):
        for record in self:
            if not record.certificado_gratuito and record.list_price <= 0.0 :
                raise ValidationError("Se requiere establecer precio")


    def _render_qweb_pdf_prepare_streams(self, report_ref, data, res_ids=None):
        report_sudo = self._get_report(report_ref)
        if 'disable_attachment' in self.env.context:
            attachment = report_sudo.attachment
            report_sudo.attachment= False
        res = super()._render_qweb_pdf_prepare_streams(report_ref = report_ref, data=data, res_ids = res_ids)
        if 'disable_attachment' in self.env.context:
            report_sudo.attachment = attachment
        return res

    def check_web_available(self, student_id, batch_id):
        self.ensure_one()
        if self.xml_id in ['isep_openeducat_reports.r_certificado1','isep_openeducat_reports.r_certificado5']:
           
           libreta = self.env['app.gradebook.student'].search([('student_id','=',student_id.id),('batch_id','=',batch_id.id)], limit=1)
           if not libreta or not libreta.state== 'closed' or  fields.Date.today <= student_id.file_closing_date:
               res = {'error_message': _('El certificado %s no puede generarse. Se requiere tener tus materias terminadas y solicitarse despues de la fecha de disertación.' %(self.display_name))
                  }
               return res
        if self.xml_id == 'isep_openeducat_reports.r_certificado4':
           libreta = self.env['app.gradebook.student'].search([('student_id','=',student_id.id),('batch_id','=',batch_id.id)], limit=1)
           if not libreta or not libreta.state== 'closed' :
               res = {'error_message': _('El certificado %s no puede generarse. Se requiere tener tus materias terminadas' %(self.display_name))
                  }
               return res

        if self.xml_id == 'isep_openeducat_reports.r_certificado6':
            #Carta no adeudo
            subscription_data = student_id.get_subscription_data()
            sale_order_ids = subscription_data.get('sale_order_ids', False)
            total_amount = subscription_data.get('t_amount_total', 0)
            total_payment = subscription_data.get('t_amount_total_payment', 0)
            total_due = subscription_data.get('t_amount_recurring_due', 0)
            t_adeuda = subscription_data.get('t_adeuda')
            if not sale_order_ids or t_adeuda == True :
                res = {'error_message': _('El certificado %s no puede generarse. Se requieren tener suscripciones activas y los pagos completos.' %(self.display_name))
                   }
                return res

        if self.xml_id == 'isep_openeducat_reports.r_certificado8':
            #Prácticas. 
            libreta = self.env['app.gradebook.student'].search([('student_id','=',student_id.id),('batch_id','=',batch_id.id)], limit=1)
            practice = self.env['practice.request'].sudo().search([('course_id.student_id','=',student_id.id),('op_admission_id','=',libreta.admission_id.id)], limit=1)
            if not practice or practice.state != 'end':
                res = {'error_message': _('El certificado %s no puede generarse. Se requiere solicitar después de tu fecha de finalización de prácticas.' %(self.display_name))
                    }
                return res

        if self.xml_id == 'isep_openeducat_reports.r_certificado7':
            #Título.
            #Condiciones para Título
            if any([not student_id.course_val, not student_id.practice_val, not student_id.payments_val, not student_id.graduated_val]):
                res = {'error_message': _('Su titulo no puede generarse. Debido a que tiene que tener cierre de expediente completo.')
                        }
                return res

        return True
