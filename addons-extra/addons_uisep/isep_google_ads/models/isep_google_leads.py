# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
import pprint
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
_logger = logging.getLogger(__name__)


class CrmFacebookFormField(models.Model):
    _name = 'isep.google.forms.field'
    _description = 'Google form fields'

    name = fields.Many2one('isep.google.forms', required=True, ondelete='cascade', string='Form')
    column_id = fields.Char(string="Column ID" )
    column_name = fields.Char(string="Column Name" )
    odoo_field = fields.Many2one('ir.model.fields',
                                 domain=[('model', '=', 'crm.lead'),
                                         ('store', '=', True),
                                         ('ttype', 'in', ('char',
                                                          'date',
                                                          'datetime',
                                                          'float',
                                                          'html',
                                                          'integer',
                                                          'monetary',
                                                          #'many2one',
                                                          'selection',
                                                          'phone',
                                                          'text'))],
                                 ondelete='set null',
                                 required=False)
    

class IsepGoogleForms(models.Model):
    _name = 'isep.google.forms'

    name = fields.Char(string='Nombre', default="/")
    form_id = fields.Char(string='Form ID')
    creative_id = fields.Char(string='Creative ID')
    team_id = fields.Many2one('crm.team', domain=['|', ('use_leads', '=', True), ('use_opportunities', '=', True)],
                              string="Sales Team")
    campaign_id = fields.Many2one('utm.campaign')
    source_id = fields.Many2one('utm.source')
    medium_id = fields.Many2one('utm.medium')
    country_id = fields.Many2one('res.country')
    mappings = fields.One2many('isep.google.forms.field', 'name')
    lead_logs = fields.One2many('isep.google.leads', 'form_id')
    company_id = fields.Many2one('res.company')
    
    

class IsepPortalLeads(models.Model):
    _name = 'isep.google.leads'

    name = fields.Char(string='Nombre', default="/")
    json = fields.Text(string='json')
    lead_id = fields.Many2one('crm.lead')
    form_id = fields.Many2one('isep.google.forms', string='Form')


    @api.model
    def create(self, values):
        res = super(IsepPortalLeads, self).create(values)
        res.name = 'LEAD/%s' % str(res.id).zfill(6)
        return res
  
    @api.model
    def _get_portal_notification_data(self, data):
        form_id = self.env['isep.google.forms'].sudo().search([('form_id', '=', data.get('form_id'))])
        if not form_id:
            form_id = self.env['isep.google.forms'].sudo().create({
                'name': data.get('form_id'),
                'form_id': data.get('form_id'),
                'creative_id': data.get('creative_id'),
            })

        new_lead_data = {
            'name': next((item['string_value'] for item in data.get('user_column_data', []) if item['column_id'] == 'FULL_NAME'), '/') or "No definido",
            'type': 'lead',
            'team_id': form_id.team_id.id,
            'campaign_id': form_id.campaign_id.id,
            'source_id': form_id.source_id.id,
            'medium_id': form_id.medium_id.id,
            'country_id': form_id.country_id.id,
            'company_id': form_id.company_id.id,
            'google_form_id': form_id.id,
            'user_id': form_id.team_id.user_id.id,        
            #'phone': next((item['string_value'] for item in data.get('user_column_data', []) if item['column_id'] == 'PHONE_NUMBER'), False),
            #'email_from': next((item['string_value'] for item in data.get('user_column_data', []) if item['column_id'] == 'EMAIL'), False),
            #'city': next((item['string_value'] for item in data.get('user_column_data', []) if item['column_id'] == 'CITY'), False),
        }

        for column_data in data.get('user_column_data', []):
            mapping = form_id.mappings.filtered(lambda m: m.column_id == column_data['column_id'])
            if mapping:
                new_lead_data[mapping.odoo_field.name] = column_data['string_value']

        try:
            lead = self.env['crm.lead'].sudo().create(new_lead_data)
            data_lead_log = {
                'json': pprint.pformat(data),
                'lead_id': lead.id,
                'form_id': form_id.id,
            }
            lead_lead_log = self.sudo().create(data_lead_log)
            lead.write({
                'google_lead_id': lead_lead_log.id,
            })
            
        except Exception as e:
            _logger.exception("No se pudo crear el cliente potencial y agregarlo al historial.: %s" % e)


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    google_form_id = fields.Many2one('isep.google.forms', string='Google Form')
    google_lead_id = fields.Many2one('isep.google.leads', string='Google Form Lead')


