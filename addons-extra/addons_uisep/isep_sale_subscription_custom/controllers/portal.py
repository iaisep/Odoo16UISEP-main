from odoo import _, http
from odoo.http import request
from odoo.addons.payment import utils as payment_utils
from odoo.addons.portal.controllers import portal


class PaymentPortal(portal.CustomerPortal):


    @http.route('/my/isep_payment_method_customer/<int:order_id>', type='http', methods=['GET'], auth='user', website=True)    
    def payment_method_isep(self,order_id, **kwargs):
        order = request.env['sale.order'].sudo().browse(order_id)
        if not order.exists():
            return request.not_found()

        partner_sudo = order.partner_invoice_id or order.partner_id
        providers_sudo = request.env['payment.provider'].sudo()._get_compatible_providers(
            request.env.company.id,
            partner_sudo.id,
            0.,  # There is no amount to pay with validation transactions.
            force_tokenization=True,
            is_validation=True,
        )

        # Get all partner's tokens for which providers are not disabled.
        tokens_sudo = request.env['payment.token'].sudo().search([
            ('partner_id', 'in', [partner_sudo.id, partner_sudo.commercial_partner_id.id]),
            ('provider_id.state', 'in', ['enabled', 'test']),
        ])

        access_token = payment_utils.generate_access_token(partner_sudo.id, None, None)
        rendering_context = {
            'providers': providers_sudo,
            'tokens': tokens_sudo,
            'reference_prefix': payment_utils.singularize_reference_prefix(prefix='V'),
            'partner_id': partner_sudo.id,
            'access_token': access_token,
            'transaction_route': '/payment/transaction',
            'landing_route': '/my/payment_method',
            **self._get_custom_rendering_context_values(**kwargs),
        }
        return request.render('payment.payment_methods', rendering_context)