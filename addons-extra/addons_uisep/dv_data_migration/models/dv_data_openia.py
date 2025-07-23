# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import xmlrpc.client
from odoo.exceptions import UserError
from bs4 import BeautifulSoup
import json
import requests
import logging
from odoo.exceptions import ValidationError
_logger = logging.getLogger(__name__)

class dvDataOpenia(models.Model):
    _name= "dv.data.openia"
    _description = 'Consulta con IA'

    def name_get(self):
        result = []
        for record in self:
            name = 'Operation IA gpt'
            result.append((record.id, name))
        return result

    model_id = fields.Many2one('dv.model.lines', 'Target Model', required=False)

    fields_old=fields.Html(string="Campos a migrar")
    fields_dest=fields.Html(string="Campos destino")
    other_tab=fields.Boolean(string="Otra tabla", help="Si no existe la tabla en la actual active para escoger la tabla destino")
    field_dest_id =fields.Many2one('ir.model', 'Modelo destino')
    ai_response = fields.Text(string="Respuesta de IA")

    company_id = fields.Many2one('res.company', string="compania")
    data_source_id = fields.Many2one('dv.data.source', string="data source")

    @api.onchange('model_id')
    def _onchange_call_models_from_remote(self):
        config_rpc = self.env['dv.data.source'].search([], limit=1)
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(config_rpc.url_rpc))
        uid = common.authenticate(config_rpc.db_rpc, config_rpc.username_rpc, config_rpc.password_rpc, {})
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(config_rpc.url_rpc))

        if not self.model_id:
            return

        filters = [['model_id', '=', self.model_id.name]]  # Asegúrate de que el filtro se ajuste al campo correcto

        fields_to_fetch = ['name', 'field_description', 'ttype', 'store', 'required','relation']

        remote_fields = models.execute_kw(config_rpc.db_rpc, uid, config_rpc.password_rpc,
                                          'ir.model.fields', 'search_read', 
                                          [filters], {'fields': fields_to_fetch})

        self.fields_old = ""
        self.ai_response = ""

        html_content = "<table border='1' class='o_list_table table table-sm table-hover position-relative table-striped'>"
        html_content += "<tr><th>Name</th><th>Field Description</th><th>Type</th><th>Stored</th><th>Relation</th></tr>"

        for field in remote_fields:
            html_content += "<tr>"
            html_content += f"<td>{field.get('name', '')}</td>"
            html_content += f"<td>{field.get('field_description', '')}</td>"
            html_content += f"<td>{field.get('ttype', '')}</td>"
            html_content += f"<td>{'Yes' if field.get('store', False) else 'No'}</td>"
            html_content += f"<td>{field.get('relation', '')}</td>"
            html_content += "</tr>"

        html_content += "</table>"

        self.fields_old = html_content

    @api.onchange('field_dest_id')
    def _onchange_and_fetch_local_model_fields2(self):
        """
        Verifica si el modelo existe en el servidor local y obtiene sus campos si existe.
        Si no existe, muestra un mensaje de error al usuario.
        """
        if not self.field_dest_id:
            return

        model_name = self.field_dest_id.model
        local_fields = self.env['ir.model.fields'].search([
            ('model', '=', model_name), 
        ])

        # if not local_fields:
        #     raise UserError(_('El modelo "%s" no existe en el servidor local.') % model_name)

        fields_data = local_fields.read(['name', 'field_description', 'ttype', 'store', 'relation'])

        self.fields_dest = ""

        html_content_local = self._generate_html_table(fields_data)

        self.fields_dest = html_content_local

    @api.onchange('model_id')
    def _onchange_and_fetch_local_model_fields(self):
        """
        Verifica si el modelo existe en el servidor local y obtiene sus campos si existe.
        Si no existe, muestra un mensaje de error al usuario.
        """
        if not self.model_id:
            return

        model_name = self.model_id.name if self.model_id else self.field_dest_id.model
        local_fields = self.env['ir.model.fields'].search([

            ('model', '=', model_name), 

        ])

        # if not local_fields:
        #     raise UserError(_('El modelo "%s" no existe en el servidor local.') % model_name)

        fields_data = local_fields.read(['name', 'field_description', 'ttype', 'store', 'relation'])

        self.fields_dest = ""

        html_content_local = self._generate_html_table(fields_data)

        self.fields_dest = html_content_local

    def _generate_html_table(self, fields_data):
        """
        Genera una tabla HTML con la información de los campos proporcionados.
        """
        html_content = "<table border='1' class='o_list_table table table-sm table-hover position-relative table-striped'>"
        html_content += "<tr><th>Name</th><th>Field Description</th><th>Type</th><th>Stored</th><th>Relation</th></tr>"

        for field in fields_data:
            html_content += "<tr>"
            html_content += f"<td>{field.get('name', '')}</td>"
            html_content += f"<td>{field.get('field_description', '')}</td>"
            html_content += f"<td>{field.get('ttype', '')}</td>"
            html_content += f"<td>{'Yes' if field.get('store', False) else 'No'}</td>"
            html_content += f"<td>{field.get('relation', '')}</td>"
            html_content += "</tr>"

        html_content += "</table>"
        return html_content
        
    # Disparador de IA
    def analyze_field_compatibility(self):        
        config = self.env['dv.data.openia.config'].search([], limit=1)
        #print("///////////////////////////////////////////////////",config.prompt)
        if not config or not config.token_gpt:
            raise UserError(_('Por favor, configure el token de la API de OpenAI en la configuración de Configuration GPT.'))
        
        fields_old_content = self._clean_html_tags(self.fields_old)
        fields_dest_content = self._clean_html_tags(self.fields_dest)
        model_origin = self.model_id.name_db
        model_name = self.model_id.name
        company_mcode= self.company_id.m_code
        company_name= self.company_id.name
        source_data= self.data_source_id.name

        prompt = (
            f"Estos son los datos=\n\n"
            f"Campo(model_origin):\n{model_origin}\n\n"
            f"Campo(model_name):\n{model_name}\n\n"
            f"Campo(company_name):\n{company_name}\n\n"
            f"Campo(company_mcode):\n{company_mcode}\n\n"
            f"Campo(source_data):\n{source_data}\n\n"
            f"Campos Origen(fields_old_content):\n{fields_old_content}\n\n"
            f"Campos Destino(fields_dest_content):\n{fields_dest_content}\n\n"
        )

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {config.token_gpt}'
        }
        
        data = {
            "model": config.model_gpt,
            "messages": [{"role": "system", "content": config.instructions_gpt}, {"role": "user", "content": prompt}],
            "temperature": config.temperature_gpt
        }

        try:            
            response = requests.post(config.url_gpt, headers=headers, data=json.dumps(data))
            response.raise_for_status()
            response_data = response.json()

            ai_response_content = response_data['choices'][0]['message']['content']
            self.ai_response = ai_response_content

        except requests.exceptions.RequestException as e:
            raise UserError(_('Error al conectar con la API de OpenAI: %s') % e)

    def _clean_html_tags(self, html_content):

        soup = BeautifulSoup(html_content, 'html.parser')
        return soup.get_text(separator="\n").strip()

    def _format_response_html(self, response_text):# Convertir el texto en párrafos HTML        
        lines = response_text.split('\n')
        html_content = '<div>'
        for line in lines:
            if line.strip():
                html_content += f'<p>{line.strip()}</p>'
        html_content += '</div>'
        return html_content

    def button_action_datatarget(self):
        self.process_json_response()
        self.ai_response = '***REGISTRO CREADO EN DATA TARGET***'
    
    def process_json_response(self): #insertar en data target el resultado IA
        for rec in self:
            try:
                json_text = rec.ai_response.strip()
                
                if json_text.startswith("```json"):
                    json_text = json_text[7:]  # Eliminar "```json\n"
                if json_text.endswith("```"):
                    json_text = json_text[:-3]  # Eliminar "```"
                print("///////////////////////////////////////2",json_text)            

                self.env['dv.data.target'].data_import_dv(json_text)
                return {
                    'type': 'ir.actions.client',
                    'tag': 'reload',
                }
            
            except (json.JSONDecodeError, ValueError) as e:
                _logger.warning("Error al decodificar el JSON: %s", e)
                raise ValidationError(_('Error al decodificar el JSON: %s') % e)

            except Exception as E:
                _logger.warning("Error al procesar la respuesta de IA: %s", E)
                raise ValidationError(_('Error al procesar la respuesta de IA: %s') % E)
    
class dvDataOpeniaConfig(models.Model):
    _name= "dv.data.openia.config"

    token_gpt=fields.Char(string='Token', copy=False, help='Coloque aca el token api que proporciona OpenIA')
    url_gpt = fields.Char(string='Url', copy=False, help='Enlace al cual se conecta la API de OpenIA', default='https://api.openai.com/v1/chat/completions')
    temperature_gpt = fields.Float(string='Temperatura chat', copy=False, help='Configura como contestara la IA. ejemplo 0.15 ofrece una respuesta directa, 1.0 nos ofrece una respuesta creativa detallada y con recomendaciones')
    model_gpt = fields.Char(string='Modelo IA', copy=False, help='Tipo de modelo de inteligencia que se utilizara aca coloca el modelo entrenado', default='gpt-4o')
    instruction_id=fields.Many2one('dv.instruction.config', string="Intrucction")
    instructions_gpt = fields.Text(string='Instrucciones', help='Coloque una breve instruccion para el asistente', copy=False, related='instruction_id.instruction')

    prompt=fields.Text(string="Prompt", help="Pront de consulta para realizar la consulta",
                       default="Revisa los siguientes campos de origen y destino y proporciona cuáles podrían ser compatibles:\n\nCampos Origen:\n{{ object.fields_old }}\n\nCampos Destino:\n{{ object.model_id.name_db }}")

class DvInstructionConfig(models.Model):
    _name= "dv.instruction.config"

    name=fields.Char(string="Reference", required=True, copy=False, readonly=True, default=lambda self: _('New'))
    comment=fields.Char(string="Comentario",required=True)
    instruction=fields.Text(string="Instruccion", required=True)
    display_name = fields.Char(string='Display Name', compute='_compute_display_name')
    
    @api.model
    def create(self,vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('dv.instruction.config') or _('New')
        res = super(DvInstructionConfig, self).create(vals)
        return res

    @api.depends('name', 'comment')
    def _compute_display_name(self):
        for employee in self:
            if employee.comment:
                employee.display_name = f'[{employee.name}] {employee.comment}'
            else:
                employee.display_name = employee.name

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('name', operator, name), ('comment', operator, name)]
        recs = self.search(domain + args, limit=limit)
        return recs.name_get()

    def name_get(self):
        result = []
        for record in self:
            name = f"{record.name} - {record.comment}"  
            result.append((record.id, name))
        return result