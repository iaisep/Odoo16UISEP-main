# -*- coding: utf-8 -*-
import base64
import logging


from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime



from odoo import models, fields, api

from odoo import models, fields, api

class PracticeRequestChecklist(models.Model):
    _name = 'practice.request.checklist'
    _description = 'Practice Request Checklist'
    _order = 'sequence, id'

    name = fields.Char(
        string="Name",
        required=True,
        help="Name of the expected activity or document."
    )
    expected_id = fields.Many2one(
        'practice.center.expected',
        string="Expected Item",
        help="Reference to the expected activity or document."
    )
    practice_request_id = fields.Many2one(
        'practice.request',
        string="Practice Request",
        required=True,
        ondelete='cascade',
        help="The practice request to which this checklist belongs."
    )
    is_completed = fields.Boolean(
        string="Is Completed?",
        default=False,
        help="Indicates if the activity or document has been completed."
    )
    is_mandatory = fields.Boolean(
        string="Is Mandatory?",
        related='expected_id.is_mandatory',
        store=True,
        help="Indicates if this activity or document is mandatory."
    )
    sequence = fields.Integer(
        string="Sequence",
        default=10,
        help="Sequence number for ordering."
    )
