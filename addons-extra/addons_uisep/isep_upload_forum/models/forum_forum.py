# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ForumForum(models.Model):
    _inherit = 'forum.forum'


    def open_wizard_upload_csv(self):
        values = {
            'id':'view_forum_csv_import_wizard_form',
            'name':u'Importar Post Forum Csv',
            'view_type':'form',
            'view_mode':'form',
            'target':'new',
            'context':{
                'get_forum_id':self.id,
            },
            'res_model':'forum.csv.import.wizard',
            'type':'ir.actions.act_window',
        }
        return values
