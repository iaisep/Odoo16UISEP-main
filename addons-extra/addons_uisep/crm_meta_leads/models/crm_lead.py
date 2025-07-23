import logging
import requests
from datetime import datetime, timedelta
from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    facebook_lead_id = fields.Char(readonly=True)
    facebook_page_id = fields.Many2one(
        'crm.facebook.page', related='facebook_form_id.page_id',
        store=True, readonly=True)
    facebook_form_id = fields.Many2one('crm.facebook.form', readonly=True)
    facebook_adset_id = fields.Many2one('utm.adset', readonly=True)
    facebook_ad_id = fields.Many2one(
        'utm.medium', related='medium_id', store=True, readonly=True,
        string='Facebook Ad')
    facebook_campaign_id = fields.Many2one(
        'utm.campaign', related='campaign_id', store=True, readonly=True,
        string='Facebook Campaign')
    facebook_date_create = fields.Datetime(readonly=True)
    facebook_is_organic = fields.Boolean(readonly=True)

    _sql_constraints = [
        ('facebook_lead_unique', 'unique(facebook_lead_id)',
         'Este cliente potencial de Facebook ya existe!')
    ]

    def get_ad(self, lead):
        ad_obj = self.env['utm.medium']
        if not lead.get('ad_id'):
            return ad_obj
        if not ad_obj.search([('facebook_ad_id', '=', lead['ad_id'])]):
            return ad_obj.sudo().create({
                'facebook_ad_id': lead['ad_id'], 'name': lead['ad_name'], }).id

        return ad_obj.search(
            [('facebook_ad_id', '=', lead['ad_id'])], limit=1)[0].id

    def get_adset(self, lead):
        ad_obj = self.env['utm.adset']
        if not lead.get('adset_id'):
            return ad_obj
        if not ad_obj.search(
                [('facebook_adset_id', '=', lead['adset_id'])]):
            return ad_obj.sudo().create({
                'facebook_adset_id': lead['adset_id'], 'name': lead['adset_name'], }).id

        return ad_obj.search(
            [('facebook_adset_id', '=', lead['adset_id'])], limit=1)[0].id

    def get_campaign(self, lead):
        campaign_obj = self.env['utm.campaign']
        if not lead.get('campaign_id'):
            return campaign_obj
        if not campaign_obj.search(
                [('facebook_campaign_id', '=', lead['campaign_id'])]):
            return campaign_obj.sudo().create({
                'facebook_campaign_id': lead['campaign_id'],
                'name': lead['campaign_name'], }).id

        return campaign_obj.search(
            [('facebook_campaign_id', '=', lead['campaign_id'])],
            limit=1)[0].id

    def prepare_lead_creation(self, lead, form):
        vals, notes = self.get_fields_from_data(lead, form)
        vals.update({
            'type': 'lead',
            'facebook_lead_id': lead['id'],
            'facebook_is_organic': lead['is_organic'],
            'name': self.get_opportunity_name(vals, lead, form),
            'description': notes,
            'team_id': form.team_id and form.team_id.id,
            'campaign_id': form.campaign_id and form.campaign_id.id, #or self.get_campaign(lead)
            'source_id': form.source_id and form.source_id.id,
            'medium_id': form.medium_id and form.medium_id.id,# or self.get_ad(lead)
            'country_id': form.country_id and form.country_id.id,
            'company_id': form.company_id and form.company_id.id,            
            'user_id': form.team_id and form.team_id.user_id and form.team_id.user_id.id or False,
            'facebook_adset_id': self.get_adset(lead),
            'facebook_form_id': form.id,
            'facebook_date_create': lead['created_time'].split('+')[0].replace('T', ' ')
        })
        return vals

    def lead_creation(self, lead, form):
        vals = self.prepare_lead_creation(lead, form)
        return self.sudo().create(vals)

    def get_opportunity_name(self, vals, lead, form):
        if not vals.get('name'):
            vals['name'] = '%s - %s' % (form.name, lead['id'])
        return vals['name']

    def get_fields_from_data(self, lead, form):
        vals, notes = {}, ''
        form_mapping = form.mappings.filtered(lambda m: m.odoo_field).mapped('facebook_field')
        unmapped_fields = []
        mapped_fields = lead.items()
        for name, value in mapped_fields:
            if name not in form_mapping:
                unmapped_fields.append((name, value))
                continue
            odoo_field = form.mappings.filtered(lambda m: m.facebook_field == name).odoo_field
            many2one_name = form.mappings.filtered(lambda m: m.facebook_field == name).many2one_name
            #notes.append('%s: %s' % (odoo_field.field_description, value))
            try:
                if odoo_field.ttype == 'many2one':
                    related_value = self.env[odoo_field.relation].search([(many2one_name, '=', value)], limit=1)
                    vals.update({odoo_field.name: related_value and related_value.id})
                elif odoo_field.ttype in ('float', 'monetary'):
                    vals.update({odoo_field.name: float(value)})
                elif odoo_field.ttype == 'integer':
                    vals.update({odoo_field.name: int(value)})
                elif odoo_field.ttype in ('date', 'datetime'):
                    vals.update({odoo_field.name: value.split('+')[0].replace('T', ' ')})
                elif odoo_field.ttype == 'selection':
                    vals.update({odoo_field.name: value})
                elif odoo_field.ttype == 'boolean':
                    vals.update({odoo_field.name: value == 'true' if value else False})
                else:
                    vals.update({odoo_field.name: value})
            except:
                pass
        # NOTE: Doing this to put unmapped fields at the end of the description
        for name, value in mapped_fields:
            notes += ('%s: %s<br/>' % (name, value))

        return vals, notes

    def process_lead_field_data(self, lead):
        field_data = lead.pop('field_data')
        lead_data = dict(lead)
        lead_data.update([(l['name'], l['values'][0])
                          for l in field_data
                          if l.get('name') and l.get('values')])
        return lead_data


    def lead_processing(self, r, form):
        # LEER https://developers.facebook.com/docs/graph-api/overview/rate-limiting/
        _logger.info('*********************** OBTENIENDO LEADS META *************************')
        _logger.info('--> 5 - '+str(r))
        _logger.info('***********************************************************************')
        if not r.get('data'):
            return
        for lead in r['data']:
            lead = self.process_lead_field_data(lead) # ok
            if not self.search([('facebook_lead_id', '=', lead.get('id')), '|', ('active', '=', True), ('active', '=', False)]):
                self.lead_creation(lead, form)
        
        # /!\ NOTE: Once finished a page let us commit that
        try:
            self.env.cr.commit()
        except Exception:
            self.env.cr.rollback()

        _logger.info('*********************** PAGING VALUE *************************')
        _logger.info(str(r.get('paging')))
        _logger.info('*********************** PAGING NEXT VALUE *************************')  
        
        if r.get('paging') and r['paging'].get('next'):
            _logger.info('Obteniendo una nueva página en el formulario: %s' % form.name)
            self.lead_processing(requests.get(r['paging']['next']).json(), form)
        form.date_retrieval = fields.datetime.now()-timedelta(hours=2)
        

        

    @api.model
    def get_facebook_leads(self):
        fb_api = "https://graph.facebook.com/v15.0/"
        for form in self.env['crm.facebook.form'].search([('active','=',True)]):
            _logger.info('Comenzando a buscar clientes potenciales desde el formulario: %s' % form.name)
            params = {'access_token': form.access_token,
                      'fields': 'created_time,field_data,ad_id,ad_name,adset_id,adset_name,campaign_id,campaign_name,is_organic',
                      'limit': '100'
                      }
            if form.date_retrieval:
                params.update({
                    'filtering': "[{'field': 'time_created', 'operator': 'GREATER_THAN', 'value': %s}]" % (int(form.date_retrieval.timestamp())),
                })
            r = requests.get(fb_api + form.facebook_form_id + "/leads", params=params).json()


            if r.get('error'):
                raise UserError(r['error']['message'])
            self.lead_processing(r, form)

        _logger.info('La búsqueda de clientes potenciales ha finalizado')
