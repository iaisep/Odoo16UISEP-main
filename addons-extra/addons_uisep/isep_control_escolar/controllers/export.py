# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields,http
from odoo.http import request
from odoo.addons.web.controllers.export import ExcelExport
import re, urllib.parse, json, base64
class ExcelExportInh(ExcelExport):

    @http.route('/web/export/xlsx', type='http', auth="user")
    def index(self, data):
        try:
            res = self.base(data)
            json_data = json.loads(data)
            model = 'model' in json_data.keys() and  json_data.get('model', False) or False
            if model in ['student.report','sep.report']:
           
                content_disposition = res.headers.get('Content-Disposition')
                filename_part = content_disposition.split(';')[1].strip()
                if filename_part.startswith('filename*=UTF-8'):
                    # Decodificar el nombre del archivo
                    filename_params = filename_part.split('=UTF-8', 2)
                    filename = filename_params[1][2:]
                    filename = urllib.parse.unquote(filename)
                    res_data = base64.b64encode(res.get_data())
                    annex = model == 'student.report' and '8' or '9'
                
                    log_values = {
                              'date':fields.Datetime.now(),
                              'user_id': request.env.uid,
                              'annex': annex,           
                             }
                    log_id = request.env['sep.report.log'].sudo().create(log_values)
                    attachment_values = {
                             'name': filename,
                             'datas': res_data,
                             'description': filename,
                             'res_model': "sep.report.log",
                             'res_id': log_id.id,
                             'type': 'binary'
                             }
                    attachment_id = request.env['ir.attachment'].sudo().create(attachment_values)
                    log_id.attachment_id = attachment_id.id
            return res
        except Exception as exc:
            _logger.exception("Exception during request handling.")
            payload = json.dumps({
                'code': 200,
                'message': "Odoo Server Error",
                'data': http.serialize_exception(exc)
            })
            raise InternalServerError(payload) from exc
