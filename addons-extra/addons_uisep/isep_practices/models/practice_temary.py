# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class PracticeTemary(models.Model):
    _name = 'practice.temary'
    _description = 'PracticeTemary'

    name = fields.Char(string='Name', size=200)
    content = fields.Text(string='Content')
    op_course_id = fields.Many2one('op.course', string="Course")
    active = fields.Boolean(default=True)