# -*- coding: utf-8 -*-

from odoo import models, fields
from babel.dates import format_date




class Certificado9Students(models.AbstractModel):
    _name = 'report.isep_openeducat_reports.t_certificado9'


    def _get_report_values(self, docids, data=None):
        # Get the model you want to report on (Optional)
        docs = self.env['op.student'].browse(docids)

        # Pass your custom values to the template
        current_date = fields.Date.today()
        date_str = format_date(current_date, format='d MMMM y', locale='es_MX')
        res = {
            'doc_ids': data and data.get('doc_ids',docids),               # Model records to display in the report
            'doc_model': data and data.get('doc_model', 'op.student'),  # Odoo model name you're working with
            'docs': data and data.get('docs',docs),               # Model records to display in the report
            'today_string': date_str,
            'base_url' :self.env['ir.config_parameter'].get_param('web.base.url')

        }
        return res



class Certificado8Students(models.AbstractModel):
    _name = 'report.isep_openeducat_reports.t_certificado8'


    def _get_report_values(self, docids, data=None):
        # Get the model you want to report on (Optional)
        docs = self.env['op.student'].browse(docids)

        # Pass your custom values to the template
        current_date = fields.Date.today()
        date_str = format_date(current_date, format='d MMMM y', locale='es_MX')
        res = {
            'doc_ids': data and data.get('doc_ids',docids),               # Model records to display in the report
            'doc_model': data and data.get('doc_model', 'op.student'),  # Odoo model name you're working with
            'docs': data and data.get('docs',docs),               # Model records to display in the report
            'today_string': date_str,
            'base_url' :self.env['ir.config_parameter'].get_param('web.base.url')

        }
        return res

class Certificado7Students(models.AbstractModel):
    _name = 'report.isep_openeducat_reports.t_certificado7'


    def _get_report_values(self, docids, data=None):
        # Get the model you want to report on (Optional)
        docs = self.env['op.student'].browse(docids)

        # Pass your custom values to the template
        current_date = fields.Date.today()
        date_str = format_date(current_date, format='d MMMM y', locale='es_MX')
        res = {
            'doc_ids': data and data.get('doc_ids',docids),               # Model records to display in the report
            'doc_model': data and data.get('doc_model', 'op.student'),  # Odoo model name you're working with
            'docs': data and data.get('docs',docs),               # Model records to display in the report
            'today_string': date_str,
            'base_url' :self.env['ir.config_parameter'].get_param('web.base.url')

        }
        return res






class Certificado6Students(models.AbstractModel):
    _name = 'report.isep_openeducat_reports.t_certificado6'


    def _get_report_values(self, docids, data=None):
        # Get the model you want to report on (Optional)
        docs = self.env['op.student'].browse(docids)

        # Pass your custom values to the template
        current_date = fields.Date.today()
        date_str = format_date(current_date, format='d MMMM y', locale='es_MX')
        res = {
            'doc_ids': data and data.get('doc_ids',docids),               # Model records to display in the report
            'doc_model': data and data.get('doc_model', 'op.student'),  # Odoo model name you're working with
            'docs': data and data.get('docs',docs),               # Model records to display in the report
            'today_string': date_str,
            'base_url' :self.env['ir.config_parameter'].get_param('web.base.url')

        }
        return res



class Certificado5Students(models.AbstractModel):
    _name = 'report.isep_openeducat_reports.t_certificado5'


    def _get_report_values(self, docids, data=None):
        # Get the model you want to report on (Optional)
        docs = self.env['op.student'].browse(docids)

        # Pass your custom values to the template
        current_date = fields.Date.today()
        date_str = format_date(current_date, format='d MMMM y', locale='es_MX')
        res = {
            'doc_ids': data and data.get('doc_ids',docids),               # Model records to display in the report
            'doc_model': data and data.get('doc_model', 'op.student'),  # Odoo model name you're working with
            'docs': data and data.get('docs',docs),               # Model records to display in the report
            'today_string': date_str,
            'base_url' :self.env['ir.config_parameter'].get_param('web.base.url')

        }
        return res



class Certificado4Students(models.AbstractModel):
    _name = 'report.isep_openeducat_reports.t_certificado4'


    def _get_report_values(self, docids, data=None):
        # Get the model you want to report on (Optional)
        docs = self.env['op.student'].browse(docids)

        # Pass your custom values to the template
        current_date = fields.Date.today()
        date_str = format_date(current_date, format='d MMMM y', locale='es_MX')
        res = {
            'doc_ids': data and data.get('doc_ids',docids),               # Model records to display in the report
            'doc_model': data and data.get('doc_model', 'op.student'),  # Odoo model name you're working with
            'docs': data and data.get('docs',docs),               # Model records to display in the report
            'today_string': date_str,
            'base_url' :self.env['ir.config_parameter'].get_param('web.base.url')
        }
        return res



class Certificado3Students(models.AbstractModel):
    _name = 'report.isep_openeducat_reports.t_certificado3'


    def _get_report_values(self, docids, data=None):
        # Get the model you want to report on (Optional)
        docs = self.env['op.student'].browse(docids)

        # Pass your custom values to the template
        current_date = fields.Date.today()
        date_str = format_date(current_date, format='d MMMM y', locale='es_MX')
        res = {
            'doc_ids': data and data.get('doc_ids',docids),               # Model records to display in the report
            'doc_model': data and data.get('doc_model', 'op.student'),  # Odoo model name you're working with
            'docs': data and data.get('docs',docs),               # Model records to display in the report
            'today_string': date_str,
            'base_url' :self.env['ir.config_parameter'].get_param('web.base.url')
        }
        return res


class Certificado2Students(models.AbstractModel):
    _name = 'report.isep_openeducat_reports.t_certificado2'


    def _get_report_values(self, docids, data=None):
        # Get the model you want to report on (Optional)
        docs = self.env['op.student'].browse(docids)

        # Pass your custom values to the template
        current_date = fields.Date.today()
        date_str = format_date(current_date, format='d MMMM y', locale='es_MX')
        res = {
            'doc_ids': data and data.get('doc_ids',docids),               # Model records to display in the report
            'doc_model': data and data.get('doc_model', 'op.student'),  # Odoo model name you're working with
            'docs': data and data.get('docs',docs),               # Model records to display in the report
            'today_string': date_str,
            'base_url' :self.env['ir.config_parameter'].get_param('web.base.url')
        }
        return res


class Certificado1Students(models.AbstractModel):
    _name = 'report.isep_openeducat_reports.t_certificado1'


    def _get_report_values(self, docids, data=None):
        # Get the model you want to report on (Optional)
        docs = self.env['op.student'].browse(docids)

        # Pass your custom values to the template
        current_date = fields.Date.today()
        date_str = format_date(current_date, format='d MMMM y', locale='es_MX')
        res = {
            'doc_ids': data and data.get('doc_ids',docids),               # Model records to display in the report
            'doc_model': data and data.get('doc_model', 'op.student'),  # Odoo model name you're working with
            'docs': data and data.get('docs',docs),               # Model records to display in the report
            'today_string': date_str,
            'base_url' :self.env['ir.config_parameter'].get_param('web.base.url')
        }
        return res

class CertifiedDiplomaStudents(models.AbstractModel):
    _name = 'report.isep_openeducat_reports.t_cert_diploma'


    def _get_report_values(self, docids, data=None):
        # Get the model you want to report on (Optional)
        docs = self.env['op.student'].browse(docids)

        # Pass your custom values to the template
        current_date = fields.Date.today()
        date_str = format_date(current_date, format='d MMMM y', locale='es_MX')
        res = {
            'doc_ids': data and data.get('doc_ids',docids),               # Model records to display in the report
            'doc_model': data and data.get('doc_model', 'op.student'),  # Odoo model name you're working with
            'docs': data and data.get('docs',docs),               # Model records to display in the report
            'today_string': date_str,
            'base_url' :self.env['ir.config_parameter'].get_param('web.base.url')
        }
        return res



