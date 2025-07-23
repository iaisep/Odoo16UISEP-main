# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class FlywireNotification(models.Model):
    _name = 'flywire.notification'
    _description = _('Flywire Notification')

    payment_id = fields.Char(string='Payment ID')
    amount_from = fields.Float(string='Amount From')
    currency_from = fields.Char(string='Currency From')
    amount_to = fields.Float(string='Amount To')
    currency_to = fields.Char(string='Currency To')
    status = fields.Char(string='Status')
    expiration_date = fields.Datetime(string='Expiration Date')
    external_reference = fields.Char(string='External Reference')
    country = fields.Char(string='Country')
    card_type = fields.Char(string='Card Type')
    card_brand = fields.Char(string='Card Brand')
    card_classification = fields.Char(string='Card Classification')
    card_expiration = fields.Char(string='Card Expiration')
    last_four_digits = fields.Char(string='Last Four Digits')
    student_id = fields.Char(string='Student ID')
    student_email = fields.Char(string='Student Email')
    student_first_name = fields.Char(string='Student First Name')
    student_last_name = fields.Char(string='Student Last Name')
    enrollment_id = fields.Char(string='Enrollment ID')
    payment_type = fields.Char(string='Payment Type')
    payment_type_other = fields.Char(string='Payment Type Other')
