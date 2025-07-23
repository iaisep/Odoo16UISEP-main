# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime



class PracticeCenterExpected(models.Model):
    _name = 'practice.center.expected'
    _description = 'Expected Activities or Documents'
    _order = 'sequence, id'  # Define el orden por defecto: primero por secuencia, luego por ID

    name = fields.Char(
        string="Name",
        required=True,
        help="Name of the expected activity or document."
    )
    expected_type = fields.Selection([
        ('activity', 'Activity'),
        ('document', 'Document')
    ], string="Expected Type", required=True, default='activity')

    practice_center_type_id = fields.Many2one(
        'practice.center.type',
        string="Practice Center Type",
        required=True,
        help="The practice center type to which this record belongs."
    )
    description = fields.Text(
        string="Description",
        help="Details or requirements of the expected activity or document."
    )
    is_mandatory = fields.Boolean(
        string="Is Mandatory?",
        default=True,
        help="Indicates if this activity or document is mandatory."
    )


    sequence = fields.Integer(
        string="Sequence",
        default=10,
        help="Sequence number for ordering."
    )

