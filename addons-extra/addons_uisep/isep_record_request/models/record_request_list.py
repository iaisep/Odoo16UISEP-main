from odoo import fields, models


class RecordRequestList(models.Model):
    _name = 'record.request.list'
    _description = 'Lista de documentos'

    name = fields.Char(string='Nombre')
    description = fields.Html(string='Descripción')
    record_request_list_line_ids = fields.One2many(comodel_name='record.request.list.line',
                                                   inverse_name='record_request_list_id')
    is_list_of_mexican_documents = fields.Boolean(default=False, string='¿Es una lista de documentos mexicanos?')
