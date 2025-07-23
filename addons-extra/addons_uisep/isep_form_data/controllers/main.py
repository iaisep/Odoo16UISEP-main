from odoo import http
from odoo.http import request
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class Main(http.Controller):

    def validar_longitug_card(self,number_card):
        if len(number_card) >= 15:
            return True
        else:
            return False

    def validar_longitug_csv(self, csv):
        if len(csv) == 3:
            return True
        else:
            return False
        
    def validar_longitud_month(self,month):
        if month <= 12: 
            return True
        else:
            return False
        
    def validar_longitud_year(self,year):
        if len(year) == 2: 
            return True
        else:
            return False


    @http.route('/card/<string:token_code>', type='http', auth="public", website=True)
    def get_card(self,token_code):
        order = request.env['res.card'].sudo().search([
            ('access_token','=',token_code),
            ('active','=',False),
            
            ])
        if order:
            _logger.info("ewewe"*20, order.partner_id.id)
            return http.request.render('isep_form_data.card', {
                'card':order
            })
        else:
            return http.request.render('isep_form_data.card_message', {})


    @http.route('/update/webcard', type="http", auth="public", website=True)
    def update_webcard(self, **kw):
        name = kw['card.name']
        partner = kw['card.partner']
        partner_id = kw['card.partner_id.id']
        number_target = kw['card.number_target']
        csv = kw['card.csv']
        date_month = int(kw['card.month'])
        date_year = kw['card.year']
        access_token = kw['card.access_token']
        card = self.validar_longitug_card(number_target)
        l_csv = self.validar_longitug_csv(csv)
        l_month = self.validar_longitud_month(date_month)
        l_year = self.validar_longitud_year(date_year)

        if not card:
            raise UserError('%s - %s' %('tarjeta inválida',number_target))
        
        if not l_csv:
            raise UserError('%s - %s' %('csv inválida', csv))

        if not l_month:        
            raise UserError('%s - %s' %('mes inválido', date_month))
        
        if not l_year:        
            raise UserError('%s - %s' %('año inválido', date_year))
        
        
        order = request.env['res.card'].sudo().search([
            ('access_token','=', access_token),
            ('active','=',False),
            ])
        order_old = request.env['res.card'].sudo().search([('partner_id','=',int(partner_id))])
        if order_old:
            order_old.write({
                'use':False})
            _logger.info("xhhhhhxx"*20, partner_id,int(partner_id),order_old)
        order.write({
            'name': name,
            'partner': partner,
            'number_target': number_target,
            'csv': csv,
            'month':date_month,
            'year':date_year,
            'active':True,
            'use':True

        })
        _logger.info("xxddddx"*20, order)
        return request.render('isep_form_data.card_thanks', {
            'card':order
        })
