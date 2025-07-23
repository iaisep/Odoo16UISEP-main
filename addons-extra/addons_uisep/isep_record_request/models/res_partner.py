from odoo import fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _ir_attachment_ids_domain(self):
        return [('public', '=', True)]

    birth_date = fields.Date('Fecha de nacimiento')
    ir_attachment_ids = fields.One2many(comodel_name='ir.attachment', inverse_name='partner_id',
                                        domain=_ir_attachment_ids_domain)

    def upload_document_list(self):
        country_id = self.country_id.id
        if country_id:
            ir_attachment_ids = []
            country = self.env['res.country'].browse(country_id)
            record_request_list_model = self.env['record.request.list']
            list_of_mexican_documents = record_request_list_model.search([('is_list_of_mexican_documents', '=', True)],
                                                                         limit=1)
            list_of_foreign_documents = record_request_list_model.search([('is_list_of_mexican_documents', '=', False)],
                                                                         limit=1)
            if country.code == 'MX' and not list_of_mexican_documents:
                raise ValidationError('¡Debes crear una Lista de documentos documentos mexicanos !!!')
            elif country.code != 'MX' and not list_of_foreign_documents:
                raise ValidationError('¡Debes crear una Lista de documentos extranjeros !!!')
            if country.code == 'MX':
                record_request_list_id = list_of_mexican_documents
            else:
                record_request_list_id = list_of_foreign_documents
            for line in record_request_list_id.record_request_list_line_ids:
                ir_attachment_ids.append((0, 0, {
                    'name': '',
                    'document': line.document,
                    'public': True,
                    'res_model': self._name,
                    'res_id': self.id
                }))
            self.write({'ir_attachment_ids': ir_attachment_ids})
