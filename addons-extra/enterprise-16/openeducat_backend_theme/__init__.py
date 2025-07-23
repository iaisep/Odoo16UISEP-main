# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from . import controllers
from . import models

from odoo import api, SUPERUSER_ID, _
from odoo.exceptions import ValidationError


def _backend_theme_pre_init(cr):
    env = api.Environment(cr, SUPERUSER_ID, {})
    web_enterprise_module = env["ir.module.module"].search(
        [('name', '=', 'web_enterprise'),
         ('state', '=', 'installed')])
    if web_enterprise_module:
        raise ValidationError(
            _("Web Enterprise Module is already installed."
              " So, You are not allowed to install this module."))
