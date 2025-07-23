from odoo import models, fields, api

class ReportInvoiceStudent(models.AbstractModel):
    _name = 'report.isep_courses_adapt.diploma_students_digital_latam'
    _description = 'Account report without payment lines'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['isep.certifies.report'].browse(docids)

        # qr_code_urls = {}
        # for invoice in docs:
        #     if invoice.display_qr_code:
        #         new_code_url = invoice._generate_qr_code()
        #         if new_code_url:
        #             qr_code_urls[invoice.id] = new_code_url

        return {
            #'doc_ids': docids,
            #'doc_model': 'account.move',
            'docs': docs.student_id,
            'batch_id':docs.batch_id,
        }
