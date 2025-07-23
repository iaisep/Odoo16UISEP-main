# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import fields, models


class WebsiteConfiguratorFeature(models.Model):
    _inherit = 'website.configurator.feature'

    active = fields.Boolean(default=True)
    is_openeducat = fields.Boolean(default=False)
    image = fields.Image(string='Image')
