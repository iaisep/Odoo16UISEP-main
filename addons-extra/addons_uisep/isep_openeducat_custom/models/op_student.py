import logging
from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class OpStudent(models.Model):
    _inherit = 'op.student'

    street = fields.Char('Calle', related="partner_id.street" , readonly=False )
    street2 = fields.Char('Calle 2', related="partner_id.street2" , readonly=False)
    phone = fields.Char('Teléfono', related="partner_id.phone" , readonly=False)
    mobile = fields.Char('Mobile', related="partner_id.mobile", readonly=False)
    email = fields.Char('Email', related="partner_id.email" , readonly=False)
    city = fields.Char('Ciudad', related="partner_id.city",  readonly=False)
    zip = fields.Char('Zip', related="partner_id.zip" , readonly=False)
    state_id = fields.Many2one('res.country.state', 'Estado', related="partner_id.state_id" , readonly=False )
    country_id = fields.Many2one('res.country', 'Päis', related="partner_id.country_id" , readonly=False )

