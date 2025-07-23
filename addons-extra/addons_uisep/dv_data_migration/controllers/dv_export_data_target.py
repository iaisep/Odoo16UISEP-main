from odoo import http
from odoo.http import request
import json

class dvDataTargetController(http.Controller):

    @http.route('/dv/export_data_targets', type='http', auth='user')
    def export_data_targets(self, ids=None):
        if ids:
            ids = list(map(int, ids.split(',')))
        else:
            return request.not_found()

        data_targets = request.env['dv.data.target'].browse(ids)
        export_data = []

        for target in data_targets:
            target_data = {
                'name': target.name,
                'sequence': target.sequence,
                'tdone': target.tdone,
                'color': target.color,
                'method': target.method,
                'model_dv_id': target.model_dv_id.name,
                'active_c_xmlrpc': target.active_c_xmlrpc,
                'data_source_id': target.data_source_id.name,
                'query': target.query,
                'allow_parcial_transaction': target.allow_parcial_transaction,
                'origin_primary_key': target.origin_primary_key,
                'target_external_id': target.target_external_id.name,
                'model_id': target.model_id.model,
                'fields': [],
                'field_noalma_fields': [],
                'note': target.note,
            }
            for field in target.field_ids:
                field_data = {
                    'origin_column': field.origin_column,
                    'origin_column_type': field.origin_column_type,
                    'field_id': field.field_id.name,
                }
                target_data['fields'].append(field_data)
            for field in target.field_noalma_ids:
                field_data = {
                    'origin_column': field.origin_column,
                    'origin_column_type': field.origin_column_type,
                    'field_id': field.field_id.name,
                }
                target_data['field_noalma_fields'].append(field_data)
            export_data.append(target_data)

        json_data = json.dumps(export_data)

        return request.make_response(json_data,
                                     headers=[
                                         ('Content-Type', 'application/json'),
                                         ('Content-Disposition', 'attachment; filename=export_data_targets.json;')
                                     ])
