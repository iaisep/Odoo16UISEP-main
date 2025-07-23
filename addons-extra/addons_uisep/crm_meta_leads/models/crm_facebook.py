import logging
import requests

from odoo import models, fields, api
from odoo.exceptions import ValidationError,UserError


_logger = logging.getLogger(__name__)

class CrmFacebookPage(models.Model):
    _name = 'crm.facebook.page'
    _description = 'Facebook Page'

    label = fields.Char(string='Page Label')
    name = fields.Char(required=True, string='Page ID')
    access_token = fields.Char(required=True, string='Page Access Token')
    form_ids = fields.One2many('crm.facebook.form', 'page_id', string='Lead Forms')

    _sql_constraints = [
        ('name_unique', 'unique(name)', 'No puedes crear una página dos veces.')
    ]

    @api.depends('label', 'name')
    def name_get(self):
        result = []
        for page in self:
            name = page.label if page.label else page.name
            result.append((page.id, name))
        return result

    def form_processing(self, r):
        if not r.get('data'):
            return
        for form in r['data']: # ok: nos retorna data en el request y el valor de r['data'] es una lista iterable, todo bien.
            form_ids = self.form_ids.filtered(lambda f: f.facebook_form_id == form['id'])
            if form_ids:
                for line in form_ids:
                    if form['status'] == 'ACTIVE':
                        line.sudo().write({
                        'active': True
                        })
                    if form['status'] == 'ARCHIVED':
                        line.sudo().write({
                        'active': False
                        })
                             
                continue
                # ok: si el id del Formulario existe no debe volver a crearlo
            
            if form['status'] == 'ACTIVE': # la consulta en si nos trae solo forms activos, asi que esta condicional se podria obviar, la dejaremos no nosefecta en nada.
                page_id = self.env['crm.facebook.form'].sudo().create({
                    'name': form['name'],
                    'facebook_form_id': form['id'],
                    'active': True,
                    'page_id': self.id})
                _logger.info('************************** ' + str(form['name']) + ' ***************************')
                _logger.info('************************** ' + str(form['id']) + ' ***************************')
                _logger.info('************************** ' + str(page_id.id) + ' ***************************')
                
                # Aqui hubo un problema, el registro se intenta crear pero se encontro campos requeridos desde el modelo que no se estan parametrizando, pasaremos el required a la vista para resolver
                # page_id.get_fields() , Esta funcion ejerce mucha carga para el timeout del request que lleva dentro, se ejecutara 1 a 1
                
        _logger.info('************************** ' + str(r.get('paging') and r['paging'].get('next')) + ' ***************************')
        if r.get('paging') and r['paging'].get('next'):
            self.form_processing(requests.get(r['paging']['next']).json())
        return


    def get_forms(self):
        r = requests.get("https://graph.facebook.com/v15.0/" + self.name + "/leadgen_forms",
                         params={'access_token': self.access_token}).json()
        # Revisamos nuestrto log para visualizar la respuesta
        _logger.info('************************** FORMULARIOS META ***************************')
        _logger.info(str(r))
        _logger.info('***********************************************************************')

        if r.get('error'):
            raise ValidationError(r['error']['message'])

        self.form_processing(r)

        
class CrmFacebookForm(models.Model):
    _name = 'crm.facebook.form'
    _description = 'Facebook Form Page'

    name = fields.Char('Nombre')
    facebook_form_id = fields.Char(required=True, string='Form ID')
    access_token = fields.Char( related='page_id.access_token', readonly=True, string='Page Access Token')
    page_id = fields.Many2one('crm.facebook.page', readonly=True, ondelete='cascade', string='Facebook Page')
    mappings = fields.One2many('crm.facebook.form.field', 'form_id')
    team_id = fields.Many2one('crm.team', domain=['|', ('use_leads', '=', True), ('use_opportunities', '=', True)],
                              string="Sales Team")
    campaign_id = fields.Many2one('utm.campaign')
    source_id = fields.Many2one('utm.source')
    medium_id = fields.Many2one('utm.medium')
    country_id = fields.Many2one('res.country')
    company_id = fields.Many2one('res.company')
    date_retrieval = fields.Datetime(string='Fetch Leads After')
    active = fields.Boolean(default=False, string="Activo")

    def get_fields(self):
        self.mappings.unlink()
        r = requests.get("https://graph.facebook.com/v15.0/" + self.facebook_form_id,
                         params={'access_token': self.access_token, 'fields': 'questions'}).json()
        
        # Revisamos nuestrto log para visualizar la respuesta
        _logger.info('***************************** Campos Meta *****************************')
        _logger.info('Hola 1 - '+str(r))
        _logger.info('***********************************************************************')

        if r.get('error'):
            raise ValidationError(r['error']['message'])
        if r.get('questions'):            
            for question in r.get('questions'):
                odoo_field = self.env['crm.facebook.form.mapping'].search([('facebook_field', '=', question['key'])], limit=1) 
                self.env['crm.facebook.form.field'].sudo().create({
                    'form_id': self.id,
                    'name': question['label'],
                    'facebook_field': question['key'],
                    'odoo_field': odoo_field.odoo_field.id or False,
                })

    def action_guess_mapping(self):
        for rec in self:
            rec.mappings.action_guess_mapping()

            
    # @api.model
    def get_facebook_leads(self):
        fb_api = "https://graph.facebook.com/v15.0/"
        for form in self:
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
            self.env['crm.lead'].lead_processing(r, form)
        _logger.info('La búsqueda de clientes potenciales ha finalizado')


class CrmFacebookFormField(models.Model):
    _name = 'crm.facebook.form.field'
    _description = 'Facebook form fields'

    form_id = fields.Many2one('crm.facebook.form', required=True, ondelete='cascade', string='Form')
    name = fields.Char()

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
                                                          'many2one',
                                                          'selection',
                                                          'phone',
                                                          'text'))],
                                 ondelete='set null',
                                 required=False)
    many2one_name_bool = fields.Boolean(compute="cp_many2one_name_bool", store=True)

    @api.depends('odoo_field')
    def cp_many2one_name_bool(self):
        for self in self:
            many2one_name_bool = False
            if self.odoo_field.ttype == 'many2one':
                many2one_name_bool = True
            self.many2one_name_bool = many2one_name_bool

    many2one_name = fields.Char('Valor a buscar' , help="Ingresar en Caso de usar un Many2one (Campos relacional)")
    facebook_field = fields.Char(required=True)


    @api.onchange('many2one_name')
    def onchange_many2one_name(self):
        for self in self:            
            if self.odoo_field.ttype=='many2one' and self.many2one_name:
                model = self.env['ir.model'].sudo().search([('model','=', self.odoo_field.relation)],limit=1)
                fields = model.field_id.filtered(lambda x: x.ttype in ('char','text','selection')).mapped('name')
                if self.many2one_name not in fields:
                    raise UserError('El campo %s debe existir dentro de la tabla %s\nLos campos disponibles son: \n%s' % (self.many2one_name , self.odoo_field.relation, fields) )
    
    def action_guess_mapping(self):
        for rec in self:
            mapping = self.env['crm.facebook.form.mapping'].search([('facebook_field', '=', rec.facebook_field)],
                                                                   limit=1)
            if mapping:
                rec.odoo_field = mapping.odoo_field

    _sql_constraints = [
        ('field_unique', 'unique(form_id, odoo_field, facebook_field)', 'Mapping must be unique per form')
    ]


class CrmFacebookFormMapping(models.Model):
    _name = 'crm.facebook.form.mapping'
    _description = 'Default field mapping for new forms'

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
                                                          'many2one',
                                                          'selection',
                                                          'phone',
                                                          'text'))],
                                 ondelete='cascade',
                                 required=True)
    facebook_field = fields.Char(required=True)

    _sql_constraints = [
        ('map_unique', 'unique(odoo_field, facebook_field)', 'Default Mapping must be unique')
    ]
