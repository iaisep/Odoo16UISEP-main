import logging
from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class OpCourse(models.Model):
    _inherit = 'op.course'

    def name_get(self):
        # Importante que la asignatura muestre su codigo para evitar confusiones
        self.browse(self.ids).read(['name', 'code'])
        return [(template.id, '%s%s' % (template.code and '%s - ' % template.code or '', template.name)) for template in self]
    
    
    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.browse()
        if name:
            recs = self.search([('name', operator, name)] + args, limit=limit)
        if not recs:
            recs = self.search([('code', operator, name)] + args, limit=limit)
        return recs.name_get()