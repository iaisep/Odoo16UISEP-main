import requests
from odoo import models, fields, api, _


class CustomAIParameter(models.Model):
    _name = 'custom_ai_parameter'
    _description = ("Configuration model for managing AI parameters. Allows selection of document types and specific "
                    "settings for OpenAI GPT integration.")
    _rec_name = "type_document_"

    # type_document = fields.Selection(
    #     [
    #         ('degree_certificate', 'Degree certificate'),
    #         ('certification_notes', 'Certification notes'),
    #         ('civil_registry', 'Civil registry')
    #     ],
    #     string="Document type",
    #     required=True)
    type_document_ = fields.Char(string="Document type", required=True)

    chat_gpt_ = fields.Boolean(string="GPT Engine", default="True")
    parameters_for_gpt = fields.Text(string='Parameters for GPT')

    @api.model
    def prueba_de_conexion(self, view=True, *args, **kwargs):
        api_key = self.env['ir.config_parameter'].search([('key', '=', 'openai_api_key')]).value
        url = "https://api.openai.com/v1/models"  # Endpoint para verificar conexión
        headers = {
            "Authorization": f"Bearer {api_key}"
        }

        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                if view:
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': 'Successful Connection',
                            'message': 'Successful connection to GPT API.',
                            'type': 'success',  # success, warning, danger
                            'sticky': False,  # True para mantener la notificación hasta que el usuario la cierre
                        },
                    }
                else:
                    return True
            else:
                error_message = "Error desconocido"
                try:
                    error_message = response.json().get('error', {}).get('message', error_message)
                except ValueError:  # Captura el error si la respuesta no es JSON
                    error_message = response.text  # Usa el texto completo del error como mensaje
                if view:
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': 'Connection error',
                            'message': _(f"Connection error: {response.status_code} - {error_message}"),
                            'type': 'warning',  # success, warning, danger
                            'sticky': False,  # True para mantener la notificación hasta que el usuario la cierre
                        },
                    }
                else:
                    return False
        except requests.exceptions.RequestException as e:
            if view:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Connection error',
                        'message': _(f"An error occurred while trying to connect to the API: {e}"),
                        'type': 'danger',  # success, warning, danger
                        'sticky': False,  # True para mantener la notificación hasta que el usuario la cierre
                    },
                }
            else:
                return False
