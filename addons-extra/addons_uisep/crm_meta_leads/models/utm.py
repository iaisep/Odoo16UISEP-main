import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class UtmMedium(models.Model):
    _inherit = 'utm.medium'

    facebook_ad_id = fields.Char('Meta Anuncio')

    _sql_constraints = [
        ('facebook_ad_unique', 'unique(facebook_ad_id)',
         'Este anuncio de Facebook ya existe!')
    ]


class UtmAdset(models.Model):
    _name = 'utm.adset'
    _description = 'Utm Adset'

    name = fields.Char()
    facebook_adset_id = fields.Char('Meta Anuncio')

    _sql_constraints = [
        ('facebook_adset_unique', 'unique(facebook_adset_id)',
         '¡Este conjunto de anuncios de Facebook ya existe!')
    ]


class UtmCampaign(models.Model):
    _inherit = 'utm.campaign'

    facebook_campaign_id = fields.Char('Meta Campaña')

    _sql_constraints = [
        ('facebook_campaign_unique', 'unique(facebook_campaign_id)',
         '¡Esta Campaña de Facebook ya existe!')
    ]
