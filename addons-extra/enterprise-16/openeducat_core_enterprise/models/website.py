# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import api, models


class Website(models.Model):
    _inherit = 'website'

    @api.model
    def configurator_init(self):
        res = super(Website, self).configurator_init()
        for vals in res['features']:
            configurator_features = self.env['website.configurator.feature'].search(
                [('id', '=', vals['id'])])
            if configurator_features.is_openeducat:
                vals.update({'is_openeducat': True})
                vals.update({'icon': ''})
                vals.update({'image': configurator_features.image})
        return res
