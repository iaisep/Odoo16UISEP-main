# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class PracticeCenterCourse(models.Model):
    _name = 'practice.center.course'
    _description = 'PracticeCenterCourse'
    _rec_name = 'op_course_id'

    op_course_id = fields.Many2one('op.course', string="Course", required=True)
    partner_id = fields.Many2one('res.partner')