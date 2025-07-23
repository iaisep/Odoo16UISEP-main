# -*- coding: utf-8 -*-
import logging
import base64
import requests

from ..exceptions.custom_exceptions import InvalidJson
from odoo.http import request

_logger = logging.getLogger(__name__)

TYPEFORM_TYPE_FILE_UPLOAD = 'file_url'
TYPEFORM_TYPE_SINGLE_CHOICE = 'choice'
TYPEFORM_TYPE_MULTIPLE_CHOICES = 'choices'


def convert_response_to_form(response):
    try:
        form = response['form_response']
        definition = form['definition']
        fields = definition['fields']
        answers = form['answers']

        form_id = form['form_id']
        submitted_at = "{} {}".format(form['submitted_at'][:10], form['submitted_at'][11:-1])
        landed_at = "{} {}".format(form['landed_at'][:10], form['landed_at'][11:-1])
        form_title = definition['title']
        form_search = request.env['mk.typeform.form'].sudo().search([('typeform_id', '=', form_id)], limit=1)

        if not form_search:
            form_search = request.env['mk.typeform.form'].sudo().create({
                'name': form_title,
                'typeform_id': form_id
            })
        typeform_id = form_search.id
        submit_form_model = create_submit_model(form_search, form_title, landed_at, submitted_at)
        # ok

        fields_ids = []
        fields_list = []
        quest_answers = {}
        extract_fields_and_references(fields, fields_list, quest_answers)
        extract_and_join_answers(answers, quest_answers)

        #_logger.info('******************************** INICIO *************************************')
        #_logger.info('answers: %s \nquest answers: %s' % (str(answers), str(quest_answers)))
        #_logger.info('******************************** FIN *************************************')
        
            
        internal_model = {}
        if 'hidden' in form:
            for name, value in form['hidden'].items():
                quest_answers[name] = {
                    'ref': name,
                    'answers': value,
                    'title': name
                }
        
        for field in quest_answers.values():
            relation_model_search = request.env['mk.typeform.model.relation'].sudo().search([
                ('reference', '=', field['ref']),
                ('form_id', '=', typeform_id),
                ('type_field', '=', 'reference_type')
            ], limit=1)
            if not relation_model_search:
                relation_model_search = request.env['mk.typeform.model.relation'].sudo().create({
                    'reference': field['ref'],
                    'form_id': typeform_id,
                    'type_field': 'reference_type'
                })
            elif relation_model_search.field_model_id:
                internal_model_search = request.env['ir.model.fields'].sudo().search([
                    ('id', '=', relation_model_search.field_model_id.id)
                ])
                if internal_model_search.ttype == 'binary' and 'file' in field:
                    internal_model[internal_model_search.name] = field['file'].datas
                elif internal_model_search.ttype in ['many2one', 'many2one_reference'] and 'file' in field:
                    internal_model[internal_model_search.name] = field['file'].id
                else:
                    internal_model[internal_model_search.name] = field['answers']
            dict_answer = {
                'title': field['title'],
                'answer': field['answers'],
                'submit_id': submit_form_model.id,
                'field_rel_id': relation_model_search.id if relation_model_search else False
            }
            if 'file' in field:
                dict_answer['file_id'] = field['file'].id
            field_model = request.env['mk.typeform.answer'].sudo().create(dict_answer)
            if field_model:
                fields_ids.append(field_model.id)

        if form_search.internal_model_id and form_search.internal_model_id.model:
            
            relation_static_search = request.env['mk.typeform.model.relation'].sudo().search([
                ('form_id', '=', form_search.id),
                ('field_model_id', '!=', False)
            ])
            for field in relation_static_search:
                if field.type_field != 'static_type':
                    if field.field_model_id.name in internal_model:
                        continue
                    for field_value in quest_answers.values():
                        if field_value['ref'] == field.reference:
                            internal_model[field.field_model_id.name] = field_value['answers']
                else:
                    internal_model[field.field_model_id.name] = eval(field.format_value)(field.value_static_field)
            """
            apoyar el desarrollo de agregar el tipo de campos de condicion
            """            
            if field.type_field == 'condition':
                #tabla de codiciones
                key_data=[]
                for key_values in field.conditon_id:
                    #dict de respuestas con ref
                    temp_key_data = []
                    for field_value in quest_answers.values():                    
                                            
                        if(field_value['ref'] == key_values.key_value_one or 
                           field_value['ref'] == key_values.key_value_two):                           
                           temp_key_data.append(field_value)
                    key_data.append(temp_key_data)
                _logger.info('key_data: %s' % (str(key_data)))
                for keyvalues in key_data:
                    for key_values in field.conditon_id:
                        if (keyvalues[0]['answers'] == key_values.value_one and 
                            keyvalues[1]['answers'] == key_values.value_two):
                            _logger.info('Campo a modificar: %s' % (str(field.field_model_id.name)))
                            _logger.info('Campo a valor: %s' % (str(key_values.result)))
                            internal_model[field.field_model_id.name]=int(key_values.result)
                            break
                
            model_id = request.env[form_search.internal_model_id.model].sudo().create(internal_model)
          
            crm_description = "" 
            if form_search.internal_model_id.model == 'crm.lead':
                for line in quest_answers.values():
                    crm_description = crm_description  + '<br/>' + line['title'] + ': ' +  line['answers']
                model_id.typeform_form_id = form_search.id
                model_id.description = crm_description

            submit_form_model.write({
                'res_internal_model_id': model_id.id,
                'res_internal_model_name': form_search.internal_model_id.model
            })

        submit_form_model.write({
            'fields_ids': [(6, 0, fields_ids)]
        })
    except Exception as e:
        logging.error(e)
        raise InvalidJson("error", e)


def extract_and_join_answers(answers, quest_answers):
    for answer in answers:
        field_answer = answer['field']
        type_answer = answer['type']
        if field_answer.get('id'):
            answer_id = field_answer['id']
            if answer_id in quest_answers:
                if type_answer in [TYPEFORM_TYPE_MULTIPLE_CHOICES, TYPEFORM_TYPE_SINGLE_CHOICE]:
                    if type_answer == TYPEFORM_TYPE_MULTIPLE_CHOICES:
                        quest_answers[answer_id]['answers'] = str(answer['choices']['labels'])
                    else:
                        quest_answers[answer_id]['answers'] = answer['choice']['label']
                elif type_answer == TYPEFORM_TYPE_FILE_UPLOAD:
                    file_url = str(answer[type_answer])
                    quest_answers[answer_id]['answers'] = file_url
                    if not file_url or len(file_url) < 4:
                        continue
                    file_name = file_url.split('/')[-1]
                    file_id = request.env['ir.attachment'].sudo().create({
                        'datas': base64.b64encode(requests.get(file_url).content),
                        'type': 'binary',
                        'name': file_name,
                    })
                    if file_id:
                        quest_answers[answer_id]['file'] = file_id
                else:
                    quest_answers[answer_id]['answers'] = str(answer[type_answer])


def extract_fields_and_references(fields, fields_list, quest_answers):
    for field in fields:
        field_id = field['id']
        if field_id not in quest_answers:
            quest_answers[field_id] = {
                'title': field['title'],
                'answers': '',
                'ref': field['ref']
            }
        fields_list.append({
            'field_id': field_id,
            'title': field['title'],
            'ref': field['ref']
        })


def create_submit_model(form_model, form_title, landed_at, submitted_at):
    return request.env['mk.typeform.submit'].sudo().create({
        'submitted_at': submitted_at,
        'landed_at': landed_at,
        'title': form_title,
        'form_id': form_model.id
    })
