# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, SUPERUSER_ID
from . import models
from . import controllers
from odoo.addons.payment import setup_provider, reset_payment_provider


def post_init_hook(cr, registry):
    setup_provider(cr, registry, 'flywire')
    # Actualización de allow_tokenization
    env = api.Environment(cr, SUPERUSER_ID, {})
    flywire_provider = env['payment.provider'].search([('code', '=', 'flywire')], limit=1)
    if flywire_provider:
        flywire_provider.show_allow_tokenization = True
        flywire_provider.support_tokenization = True
        flywire_provider.allow_tokenization = True  # Cambia el valor a True


def uninstall_hook(cr, registry):
    # Desactivar allow_tokenization al desinstalar el módulo
    env = api.Environment(cr, SUPERUSER_ID, {})
    flywire_provider = env['payment.provider'].search([('code', '=', 'flywire')], limit=1)
    if flywire_provider:
        flywire_provider.show_allow_tokenization = False
        flywire_provider.support_tokenization = False
        flywire_provider.allow_tokenization = False  # Restablece el valor a False