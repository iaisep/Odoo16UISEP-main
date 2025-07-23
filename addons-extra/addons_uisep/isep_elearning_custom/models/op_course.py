import logging
from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class OpCourse(models.Model):
    _inherit = 'op.course'

    slide_channel_ids = fields.Many2many(
        string='Asignatura Complementaria',
        comodel_name='slide.channel',
        relation='elearning_openeducat',
        column1='elearning',
        column2='openeducat',
    )
    


    @api.model
    def _lang_get(self):
        return self.env['res.lang'].get_installed()

    lang = fields.Selection(_lang_get, string='Idioma', required=True, help="All the emails and documents sent to this contact will be translated in this language.")