# -*- coding: utf-8 -*-

from odoo import models, fields
from babel.dates import format_date



class CertificadoPractices(models.AbstractModel):
    _name = 'report.isep_practices_2.t_practices'


    def _get_report_values(self, docids, data=None):
        # Get the model you want to report on (Optional)
        docs = self.env['practice.request'].browse(docids)

        # Pass your custom values to the template
        current_date = fields.Date.today()
        date_str = format_date(current_date, format='d MMMM y', locale='es_MX')
        res = {
            'doc_ids': data and data.get('doc_ids',docids),               # Model records to display in the report
            'doc_model': data and data.get('doc_model', 'practice.request'),  # Odoo model name you're working with
            'docs': data and data.get('docs',docs),               # Model records to display in the report
            'today_string': date_str,
            'base_url' :self.env['ir.config_parameter'].get_param('web.base.url')
        }
        return res


