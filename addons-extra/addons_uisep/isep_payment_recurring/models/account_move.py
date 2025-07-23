# -*- coding: utf-8 -*-
import logging
import requests
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons.isep_payment_recurring.controllers.main import Main
from odoo import http
from werkzeug import urls

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'


    def open_wizard_url_flywire(self):
        values = {
            'id':'isep_form_data_wizard_view',
            'name':u'Link de Sesion Flywire',
            'view_type':'form',
            'view_mode':'form',
            'target':'new',
            'context':{
                'get_invoice_id':self.id,
            },
            'res_model':'isep.payment.recurring.wizard',
            'type':'ir.actions.act_window',
        }
        return values

    
    def create_flywire_session(self):
        self.ensure_one()
        session_flywire = self.env['data.flywire'].sudo().search([('active', '=', True)], limit=1)
        base_url = self.get_base_url()
        # webhook_url = urls.url_join(base_url, Main._url_webhook_recurring)
        default_webhook_url = urls.url_join(base_url, Main._url_webhook_recurring)
        webhook_url = session_flywire.url_website_webhook if session_flywire.active_url_website_webhook else default_webhook_url
        _logger.info("222"*100, webhook_url)

        if not session_flywire or not self:
            return False, 'Flywire session or invoice not found.'

        api_key = session_flywire.api_key
        url = session_flywire.url_create_session

        headers = {
            "X-Authentication-Key": api_key,
            "Content-Type": "application/json"
        }

        payload = {
            "type": "tokenization_and_pay",
            "charge_intent": {"mode": "unscheduled"},
            "payor": {
                "first_name": self.partner_id.name,
                "last_name": "",
                "address": self.partner_id.contact_address,
                "city": self.partner_id.city,
                "country": self.partner_id.country_id.name,
                "state": self.partner_id.state_id.name,
                "phone": self.partner_id.phone,
                "email": self.partner_id.email,
                "zip": self.partner_id.zip
            },
            "options": {"form": {"action_button": "save", "locale": "en"}},
            "recipient": {
                "fields": [{
                    "id": "student_id",
                    "value": str(self.partner_id.id).zfill(8)
                    }]},
            "items": [{
                "id": "default", 
                "amount": int(self.amount_residual * 100), 
                "description": "Invoice Payment"}],
            "notifications_url": webhook_url,
            "external_reference": "1234-reference",
            "recipient_id": "IUS",
            "schema": "cards",
            "payor_id": "payor_test"
        }

        response = requests.post(url, headers=headers, json=payload)
        response_json = response.json()
        hosted_form_url = response_json.get('hosted_form', {}).get('url', '')

        _logger.info("*"*40)
        _logger.info(response_json)
        if hosted_form_url:
            return True, hosted_form_url
        else:
            _logger.error("No se pudo encontrar la URL del formulario alojado en la respuesta.")
            return False, 'No hosted form URL found in response.'

        
    
    def confirm_flywire_session(self, confirm_url):
        session_flywire = self.env['data.flywire'].sudo().search([('active', '=', True)], limit=1)
        if not session_flywire:
            return {'status': 'error', 'message': 'No active Flywire session found'}

        api_key = session_flywire.api_key        
        _logger.info("urlll"*100,confirm_url)
        url = confirm_url
    
        headers = {
            "X-Authentication-Key": api_key,
            "Content-Type": "application/json"
        }


        response = requests.post(url, headers=headers)
        response_json = response.json()

        if response.status_code == 200:
            _logger.info("payment_method"*20,response_json.get('payment_method'),response_json.get('mandate') )
            return {'status': 'success', 'payment_method': response_json.get('payment_method'), 'mandate': response_json.get('mandate')}
        else:
            return {'status': 'error', 'message': response_json.get('message', 'Error confirming session')}


    def create_flywire_payment(self, payment_method, mandate):
        session_flywire = self.env['data.flywire'].sudo().search([('active', '=', True)], limit=1)
        base_url = self.get_base_url()
        # webhook_url = urls.url_join(base_url, Main._url_webhook_recurring)
        default_webhook_url = urls.url_join(base_url, Main._url_webhook_recurring)
        webhook_url = session_flywire.url_website_webhook if session_flywire.active_url_website_webhook else default_webhook_url
        if not session_flywire:
            return {'status': 'error', 'message': 'No active Flywire session found'}

        api_key = session_flywire.api_key
        url = session_flywire.url_create_payment
        headers = {
            "X-Authentication-Key": api_key,
            "Content-Type": "application/json"
        }

        payload = {
            "charge_intent": {"mode": "unscheduled"},
            "mandate_id": mandate,
            "payment_method_token": payment_method,
            "payor_id": "payor_test",
            "recipient": {
                "id": "IUS",
                "fields": [
                    {"id": "student_id", "value": str(self.partner_id.id).zfill(8)},
                    {"id": "student_first_name", "value": "John"},
                    {"id": "student_last_name", "value": "Doe"}
                ]
            },
            "items": [{
                "id": "default", 
                "amount": int(self.amount_residual * 100)}],
            "metadata": {"Internal-ID": "12345", "Int-Comment": "A comment about this payment"},
            "notifications_url": webhook_url,
            "external_reference": "1234-reference"
        }

        response = requests.post(url, headers=headers, json=payload)
        response_json = response.json()

        # if response.status_code == 200:
        _logger.info('status', response.status_code, response_json)
        return {'status': 'success', 'payment': response_json}
        # else:
        #     _logger.info("status", response.status_code)
        #     return {'status': 'error', 'message': response_json.get('message', 'Error creating payment')}
