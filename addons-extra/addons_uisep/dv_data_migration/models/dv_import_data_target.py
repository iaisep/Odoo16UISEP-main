import base64
import logging
from odoo import api, fields, models,_
from odoo.exceptions import ValidationError
_logger = logging.getLogger(__name__)

class dvDataImport(models.TransientModel):
    _name = 'dv.data.import'
    _description = 'Import data migration'

    data_import_dv = fields.Binary(string="Upload JSON", attachment=True)

    def ks_do_action(self):
        for rec in self:
            try:
                ks_result = base64.b64decode(rec.data_import_dv)
                self.env['dv.data.target'].data_import_dv(ks_result)
                return {
                    'type': 'ir.actions.client',
                    'tag': 'reload',
                }
            except Exception as E:
                _logger.warning(E)
                raise ValidationError(_(E))