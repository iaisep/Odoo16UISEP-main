# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from bs4 import BeautifulSoup
import logging
import requests
import json
import numpy as np
import openai
from datetime import datetime, timedelta

_logger = logging.getLogger( __name__ )

class HelpdeskTicket(models.Model):
    _inherit= "helpdesk.ticket"

    message_temp_gpt=fields.Text(string="ultimo Mensaje ia", copy=False)

    model_content = fields.Html(string='llamado modelo',copy=False)    
    consult_gpt = fields.Boolean(related='team_id.consult_gpt')
    consult_consult_gpt = fields.Boolean(related='team_id.consult_consult_gpt')
    acti_state_ia = fields.Boolean(related='stage_id.acti_state_ia')
    field_send_gpt = fields.Char(string='Espacio reenvio')
    
    def mensaje_chatgpt(self): # Funcion limpia el mensaje que se recibe, tratamos de limpiar y tomar solo el contenido del correo con el parser
        mensajes = self.env['mail.message'].sudo().search([
            ('model', '=', 'helpdesk.ticket'), 
            ('res_id', '=', self.id),
            ('message_type', 'in', ('email','comment'))], #
            order='id asc')  
        textos_mensajes = []
        parser_configs = self.team_id.mail_parser_ids
        if mensajes:
            for mensaje in mensajes:
                found = False
                for config in parser_configs:                    
                    soup = BeautifulSoup(mensaje.body, 'html.parser')
                    texto_interes = soup.find(config.tag, {config.attribute: config.attribute_value}) if config.attribute and config.attribute_value else soup.find(config.tag)                                   
                    if texto_interes: 
                        texto = texto_interes.text.strip() if texto_interes.text.strip() else str(mensaje.subject)
                        author = mensaje.type_message_role if mensaje.author_id else ""
                        textos_mensajes.append(f"{author}: {texto}")
                        found = True
                        break    
                if not found:                    
                    author = mensaje.type_message_role if mensaje.author_id.name else ""
                    textos_mensajes.append(f"{author}: [Contesta: Tenemos unos inconvenientes vuelve intentarlo mas tarde]")                      
        else:            
            author = "user"
            mensaje = str(self.description) if str(self.description) else str(self.name)
            textos_mensajes.append(f"{author}: {mensaje}")
        return textos_mensajes

    def action_send_response_gpt(self):#    
        for rec in self:
            ctx = {}    
            email_list = rec.partner_email  
            odoo_bot_partner = self.env.ref('base.partner_root')
            if email_list:
                ctx['email_to'] = email_list
                ctx['email_from'] = self.team_id.display_alias_name if self.team_id.display_alias_name else self.company_id.email
                ctx['send_email'] = True
                ctx['attendee'] = rec.partner_name
                ctx['name'] = rec.name
                template = self.env.ref('connect_chatgpt.email_template_response_ia_gpt')
                template.with_context(ctx).send_mail(self.id, force_send=True, raise_exception=False)

                last_message = self.env['mail.message'].search([
                    ('res_id', '=', self.id),
                    ('model', '=', 'helpdesk.ticket')], 
                    order='date desc', limit=1)                
                if last_message:
                    last_message.type_message_role = 'assistant'
                    last_message.author_id = odoo_bot_partner.id
                    last_message.subtype_id = 1     
            self.message_temp_gpt = "" 
            if self.model_content != '':
                self.model_content = ""   
                self.field_send_gpt = False  

    def cosine_similarity(self, vec1, vec2): #Calcula la similitud entre pregunta y los embeding generados.         
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        #print("Longitud de vec1:", len(vec1))
        #print("Contenido de vec1:", vec1)
        #print("Longitud de vec2:", len(vec2))
        #print("Contenido de vec1:", vec2)
        similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
        return similarity
  
    
    def find_most_relevant_passage(self, question_embedding):#Encuentra el pasaje más relevante de convert basado en la similitud        
        highest_similarity = -1
        most_relevant_passage = None
        articles = self.team_id.article_embeding_ids
        slides = self.team_id.slide_slide_ids
        most_relevant_passage1= None
        most_relevant_passage2 = None
        if articles:            
            for article in articles:
                if article.embeddings_json:
                    article_embedding = json.loads(article.embeddings_json)
                    similarity = self.cosine_similarity(question_embedding, article_embedding)
                    if similarity > highest_similarity:
                        highest_similarity = similarity
                        most_relevant_passage1 = article.convert
        if slides:            
            for article in slides:
                if article.embeddings_json:
                    article_embedding = json.loads(article.embeddings_json)
                    similarity = self.cosine_similarity(question_embedding, article_embedding)
                    if similarity > highest_similarity:
                        highest_similarity = similarity
                        most_relevant_passage2 = article.convert
        if most_relevant_passage1:
            most_relevant_passage = most_relevant_passage1
        if most_relevant_passage2:
            most_relevant_passage = most_relevant_passage2        
        return most_relevant_passage 

    def generate_embedding(self,question):
        if self.team_id.article_embeding_ids or self.team_id.slide_channel_ids:
            config = self.env['config.openia.embedding'].search([], limit=1)     
            api_key = config.api_key
            model_gpt = config.model_gpt if config.model_gpt else 'text-embedding-ada-002'        
            openai.api_key = api_key
            response = openai.Embedding.create(input=question, model=model_gpt)
            embedding = response['data'][0]['embedding']
            return embedding
   
    def call_assistant_ia(self): 
        token = self.team_id.token_gpt
        url = self.team_id.url_gpt
        temperature = self.team_id.temperature_gpt
        model = self.team_id.model_gpt
        instrucctions = self.team_id.instructions_gpt
        finish_phrase = self.team_id.finish_gpt_ids        
        max_tokens = self.team_id.max_tokens_gpt         
        self.model_content = ""
        activate_preview_gpt = self.consult_gpt
        model_content = self.call_model_consult()
        text_mensajes = self.mensaje_chatgpt() 
        question_today = str(self.field_send_gpt) 
        most_relevant_passage = None

        if self.team_id.article_embeding_ids or self.team_id.slide_channel_ids:
            question = question_today 
            question_embedding = self.generate_embedding(question)  
            most_relevant_passage = self.find_most_relevant_passage(question_embedding)

        messages = [{"role": "system", "content": instrucctions}] if instrucctions else []
        if most_relevant_passage:
            messages.append({"role": "user", "content": most_relevant_passage})

        if model_content:        
            messages.append({"role": "user", "content": "Toma estos datos y espera a que te pregunte de estos. "+str(model_content)})
            messages.append({"role": "assistant", "content": "Entiendo cuando lo pidas, te dare la informacion de forma concisa."})
        for texto in text_mensajes:
            if ": " in texto: 
                role, content = texto.split(": ", 1)
                role = role.lower() 
                messages.append({"role": role, "content": content})     
        if self.field_send_gpt:
            messages.append({"role": "assistant", "content":  str(self.message_temp_gpt)})
            messages.append({"role": "user", "content": question_today})

        payload = json.dumps({
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens 
        })
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload)       
        if response.status_code == 200:
            respuesta_json = response.json()
            if respuesta_json.get("choices"):
                first_choice = respuesta_json["choices"][0]
                message = first_choice.get("message", {})
                content = message.get("content", "")
                self.message_temp_gpt = content  
                if activate_preview_gpt != True:
                    self.action_send_response_gpt()

                finish_gpt_phrases = finish_phrase.mapped('name')
                self.field_send_gpt = False
                if any(finish_gpt_phrase.lower() in payload.lower() for finish_gpt_phrase in finish_gpt_phrases):
                    self.ticket_close_gpt()
            else:
                self.message_temp_gpt = "No se encontró información relacionada."
                self.field_send_gpt = False
        else:
            _logger.info(response.text)

    
    def message_post(self, **kwargs): # Esta funcion la heredamos (cuando se recibe un correo se dispara esta funcion y pega el mensaje/correo al ticket) capturamos para ejecutar la api
        result = super(HelpdeskTicket, self).message_post(**kwargs) 
        odoo_bot_partner = self.env.ref('base.partner_root')
        try:
            if result.message_type in ('email','comment','auto_comment') and self.team_id.activate_gpt == True and self.stage_id.acti_state_ia == True and result.author_id == self.partner_id:                
                self.call_assistant_ia()
            elif result.message_type != 'notification' and self.team_id.activate_gpt and self.stage_id.acti_state_ia and self.team_id.use_website_helpdesk_form and (result.author_id == self.partner_id or result.author_id == odoo_bot_partner):
                self.call_assistant_ia()
            elif result.message_type == 'notification' and self.team_id.activate_gpt and self.stage_id.acti_state_ia and self.team_id.use_website_helpdesk_form:
                self.call_assistant_ia()
        except Exception:
            pass
        return result
    
    def ticket_close_gpt(self):
        stage = self.team_id.stage_id
        for rec in self:            
            if stage:
                rec.update({
                    'stage_id': stage.id,
                })

    def ticket_cron_autoclose_gpt(self): 
        tickets = self.search([])       
        for ticket in tickets: 
            if ticket.team_id.activate_gpt == True and ticket.stage_id.acti_state_ia == True:
                stage = ticket.team_id.stage_id
                autoclose = ticket.team_id.activate_autoclose
                if stage and autoclose == True:          
                    ticket.update({
                        'stage_id': stage.id,
                    })

    from datetime import datetime, timedelta

    def ticket_cron_autoclose_gpt48(self): 
        tickets = self.search([
            ('team_id.activate_gpt', '=', True),  
            ('stage_id.acti_state_ia', '=', True),  
            ('team_id.activate_autocancel', '=', True) 
        ]) 
        for ticket in tickets:
            last_message = ticket.message_ids.filtered(lambda m: m.type_message_role == 'assistant').sorted(key=lambda m: m.date, reverse=True)[:1]
            if last_message:
                last_message_date = last_message.date
                if last_message_date and (datetime.now() - last_message_date) > timedelta(hours=48):
                    stage = ticket.team_id.stage_cancel_id
                    if stage:
                        ticket.update({
                            'stage_id': stage.id, 
                        })

    
    def call_model_consult(self): #querys
        model_content = ""
        contenido = ""
        for record in self:
            if not record.partner_id:
                model_content = "No se encontró información relacionada."
                continue
            
            for config in record.team_id.config_consult_ids:
                text_content = ""
                joins = ""
                filter = ""
                model = self.env['ir.model'].browse(config.model_id.id).model
                partner_field = config.rel_field_id.name                
                table_name = self.env[model]._table                    
                fields_and_titles = []                
                joined_tables = {}
                filter_state =config.state_field_id.name
                state_content=config.state_content
                filter_state_two =config.filter_field_id.name
                filter_content=config.filter_content
                consul_consul=self.consult_consult_gpt
                if filter_state:
                    filter = f" AND {table_name}.\"{filter_state}\" = '{state_content}'"
                if filter_state and filter_state_two:
                    filter = f" AND {table_name}.\"{filter_state}\" = '{state_content}' AND {table_name}.\"{filter_state_two}\" = '{filter_content}'"
                for line in config.config_consul_line_ids:
                    if line.fields_ids.name:
                        if line.followone_field_id:
                            related_table = self.env[line.fields_ids.relation]._table
                            related_field = line.followone_field_id.name
                            alias = f"{related_table}"
                            
                            if alias not in joined_tables:
                                joins += f" LEFT JOIN {related_table} ON {table_name}.{line.fields_ids.name} = {alias}.id"
                                joined_tables[alias] = True
                            fields_and_titles.append((f"{alias}.\"{related_field}\" AS \"{line.name}\"", line.name))
                        else:  
                            fields_and_titles.append((f"{table_name}.\"{line.fields_ids.name}\"", line.name))
            
                if not fields_and_titles:
                    continue

                fields = [ft[0] for ft in fields_and_titles]
                titles = [ft[1] for ft in fields_and_titles]
                query = f"""
                    SELECT {', '.join(fields)}
                    FROM {table_name}
                    {joins}
                    WHERE {partner_field} = %s
                    {filter}
                """
                self.env.cr.execute(query, (record.partner_id.id,))
                result = self.env.cr.fetchall()

                text_content += f"[{config.name}\n"
                text_content += "|".join(titles) + "\n"
                for row in result:
                    text_content += "|".join(map(str, row)) + "\n"
                text_content += "]"+"\n"

                model_content += text_content

                if consul_consul == True:
                    html_content = f"<h3>{config.name}</h3><table border='1' style='border-collapse: collapse;'><thead><tr>"
                    for _, title in fields_and_titles:
                        html_content += f"<th style='border: 1px solid black; padding: 5px;'>{title}</th>"
                    html_content += "</tr></thead><tbody>"
                    for row in result:
                        html_content += "<tr>" + "".join(f"<td style='border: 1px solid black; padding: 5px;'>{val}</td>" for val in row) + "</tr>"
                    html_content += "</tbody></table>"
                    contenido += html_content
                    self.model_content = contenido  
                else:
                    pass                  

        return model_content
    

   