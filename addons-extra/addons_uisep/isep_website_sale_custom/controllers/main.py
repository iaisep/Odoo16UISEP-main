from odoo import fields, http, SUPERUSER_ID, tools, _
import logging
from odoo.addons.website_sale.controllers.main import WebsiteSale, WebsiteSaleForm
from odoo.http import request
from dateutil.relativedelta import relativedelta
_logger = logging.getLogger(__name__)
from odoo.exceptions import AccessError, MissingError, ValidationError
import json
from odoo.addons.base.models.ir_qweb_fields import nl2br
import pprint
    
from odoo.addons.website_sale.controllers.main import WebsiteSale

    

class CustomWebsiteSaleForm(WebsiteSaleForm):
       
    
    @http.route('/website/form/shop.sale.order', type='http', auth="public", methods=['POST'], website=True)
    def website_form_saleorder(self, **kwargs):
        model_record = request.env.ref('sale.model_sale_order')
        try:
            data = self.extract_data(model_record, kwargs)
            _logger.info('********** DATA WEB: %s' % pprint.pformat(data))  # debug
        except ValidationError as e:
            return json.dumps({'error_fields': e.args[0]})

        order = request.website.sale_get_order()
        if data['record']:
            order.write(data['record'])

        # Garantizamos con isep_custom_form_shop y shop.sale.order que es el formulario que queremos tratar
        # Vamos a obviar el grabado de informacion cuando el usuario es public, User Public siempre es el ID 4
        # No deberia pasar este caso ya que se genera un usuario nuevo pero igual lo tratamos y mandamos la info al chatter
        if 'isep_custom_form_shop' not in data['custom'] or order.partner_id.id == 4:  
            if data['custom']:
                values = {
                    'body': nl2br(data['custom']),
                    'model': 'sale.order',
                    'message_type': 'comment',
                    'res_id': order.id,
                }
                request.env['mail.message'].with_user(SUPERUSER_ID).create(values)
        else:
            if data['custom']:
                order.sudo()._process_custom_form(order.partner_id,data['custom'] )

        if data['attachments']:
            self.insert_attachment(model_record, order.id, data['attachments'])

        return json.dumps({'id': order.id})
    
  


class CustomWebsiteSale(WebsiteSale):  

    # Haciendo requerido el Vat
    #def _get_mandatory_fields_billing(self, country_id=False):
    #    result = super()._get_mandatory_fields_billing(country_id)
    #    result.append("vat")
    #    return result

    
    @http.route(['/shop/confirm_order'], type='http', auth="public", website=True, sitemap=False)
    def confirm_order(self, **post):
        res = super(CustomWebsiteSale, self).confirm_order(**post)
        try:       
            order = request.website.sale_get_order()
            if not order.subscription_schedule and order.partner_id.id != 4:
                order.sudo()._auto_scheduled_order()
        except:
            pass
        
        return res
    
    
    @http.route(['/shop/address'], type='http', methods=['GET', 'POST'], auth="public", website=True, sitemap=False)
    def address(self, **kw):
        res = super(CustomWebsiteSale, self).address(**kw)
        order = request.website.sale_get_order()
        try:            
            if not order.subscription_schedule and order.partner_id.id != 4:
                order.sudo()._auto_scheduled_order()
        except:
            pass        
    
        return res
    
    
    @http.route(['/shop/extra_info'], type='http', methods=['GET', 'POST'], auth="public", website=True, sitemap=False)
    def extra_info(self, **post):
        res = super(CustomWebsiteSale, self).extra_info(**post)
        order = request.website.sale_get_order()       
        
        try:       
            order.sudo().get_academic_product_template_id()
        except:
            pass
        
        return res
    
    