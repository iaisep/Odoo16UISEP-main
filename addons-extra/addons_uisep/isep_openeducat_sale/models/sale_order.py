import logging
from odoo import models, fields, api, http
from odoo.exceptions import UserError, ValidationError , AccessError
from werkzeug.wrappers import Response
from dateutil.relativedelta import relativedelta
import json
_logger = logging.getLogger(__name__)
from odoo.http import content_disposition, request
from odoo.tools.misc import html_escape
import werkzeug.exceptions
from datetime import datetime
from werkzeug.urls import url_parse

class SaleOrder(models.Model):
    _inherit = 'sale.order'    

    
    admission_register_id = fields.Many2one('op.admission.register', string="Registro de Admisión" , copy=False )
    admission_id = fields.Many2one('op.admission', string="Admisión" , copy=False )

    admission_date = fields.Date(string="Fecha de Inicio",  copy=False )
    period = fields.Char(string="Periodo de Admisión", compute="_compute_period", store=True,  copy=False)
    
    
    error_admission = fields.Boolean(string="Error en el proceso",  copy=False )
    error_admission_msn = fields.Html(string="Error en el proceso, detalle",  copy=False )
    
    product_template_id = fields.Many2one('product.template', string="Producto",  copy=False)
    course_id = fields.Many2one('op.course', string="Curso",  copy=False)
    
    gender = fields.Selection(
        [('m', 'Masculino'), ('f', 'Femenino'), ('o', 'Otro')],
        string='Género'
        )
    
    @api.onchange('error_admission')
    def onchange_error_admission(self):
        for record in self:
            if record.error_admission == False:
                record.error_admission_msn = ''
        
    
    def ad_auto_email_welcome(self,order):
        try:
            order.admission_id.send_mail_view()
        except Exception as e:
            order.error_admission = True
            prev_msg = order.error_admission_msn or ''            
            error_str = str(e)[:500]
            new_msg = f"<p><b>Auto email error:</b> {error_str}</p>"
            order.error_admission_msn = prev_msg + new_msg
    
    def ad_state_admission_done(self, order):
        try:
            order.admission_id.submit_form()
            order.admission_id.confirm_in_progress()
            order.admission_id.admission_confirm()
            order.admission_id.enroll_student()
        except Exception as e:
            order.error_admission = True
            prev_msg = order.error_admission_msn or ''
            error_str = str(e)[:500]
            new_msg = f"<p><b>Estado de admision error:</b> {error_str}</p>"
            order.error_admission_msn = prev_msg + new_msg            
    
    def auto_ad_active(self):
        ad = self.env['auto.admission.required'].search([], limit=1)
        
        lang = self.course_id.lang if self.course_id else False
        auto_ad = False
        if lang == 'es_MX' and ad.mx_active:
            auto_ad = True
        if lang == 'pt_BR' and ad.br_active:
            auto_ad = True
            
        return auto_ad
    
    
    def _action_confirm(self):
        res = super(SaleOrder, self)._action_confirm()
        for order in self:
            
            ad = self.env['auto.admission.required'].search([], limit=1)
            
            lang = self.course_id.lang if self.course_id else False
            auto_ad = self.auto_ad_active()
            
            if auto_ad:
                if not order.product_template_id or not order.course_id:
                    order.get_academic_product_template_id()
                if order.period and order.product_template_id:
                    order.get_register_id(order.period, order.product_template_id )
                if order.admission_register_id:   
                    order.get_admision_id(order.admission_register_id)
                            
                
                if self.course_id and lang == 'es_MX':
                    if ad.mx_auto_email_welcome:
                        order.ad_auto_email_welcome(order)
                    if ad.mx_state_admission_done:
                        order.ad_state_admission_done(order)
                
                if self.course_id and lang == 'pt_BR':
                    if ad.br_auto_email_welcome:
                        order.ad_auto_email_welcome(order)
                    if ad.br_state_admission_done:
                        order.ad_state_admission_done(order)
                     
        return res
    
    # Si actualizan aqui, tambien actualizar _compute_period
    def gat_date_max_register(self, periodo):
        fechas_fin = {
            "01": "04-30",
            "02": "08-31",
            "03": "12-31"
        }
        anio, cod_periodo = periodo.split("-")
        if cod_periodo not in fechas_fin:
            raise ValueError("Periodo no valido. Solo se permiten: 01, 02, 03")
        fecha_str = f"{anio}-{fechas_fin[cod_periodo]}"
        return datetime.strptime(fecha_str, "%Y-%m-%d").date()
        
        
    
    # se invoca al cargar el formulario /shop/extra_info
    def get_academic_product_template_id(self):
        for record in self:
            error_admission_msn = []
            order_line = self.order_line.filtered(lambda x: x.product_template_id.is_academic_program and x.product_template_id.recurring_invoice )
            if order_line:
                for line in order_line:
                    course_id = self.env['op.course'].search([('product_template_id', '=', line.product_template_id.id )], limit=1)
                    
                    if course_id:
                        record.product_template_id = course_id.product_template_id
                        record.course_id = course_id.id
                    else:
                        error_admission_msn.append("* El programa académico %s debe asociarse con el curso, comunicate con un asesor." % line.product_template_id.name)
            
            if error_admission_msn:
                record.error_admission_msn = '\n'.join(error_admission_msn)
                record.error_admission = True
            else:
                record.error_admission_msn = False
                record.error_admission = False
                
            
    
    def action_admission_register(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'op.admission.register',
            'res_id': self.admission_register_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    # Si actualizan aqui, tambien actualizar gat_date_max_register
    @api.depends('admission_date')
    def _compute_period(self):
        for record in self:
            period = False
            if record.admission_date:
                year = record.admission_date.year
                month = record.admission_date.month
                if month in (1, 2, 3, 4):
                    period = f'{year}-01'
                elif month in (5, 6, 7, 8):
                    period = f'{year}-02'
                elif month in (9, 10, 11, 12):
                    period = f'{year}-03'
            record.period = period

    def action_view_admission(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'op.admission',
            'res_id': self.admission_id.id,
            'view_mode': 'form',
            'target': 'current',
        }


    # op.admission.register
    # El filtro admission_register_id debe ser por state product_template_id period - ok 
    # Esta funcion debe ejecutarse al confirmar la venta solo si period y product_template_id estan establecidos
    
    def action_get_register_id(self):
        auto_ad = self.auto_ad_active()
        if auto_ad:
            self.get_register_id(self.period,self.product_template_id)
        
    def get_register_id(self, period, product_template_id ):
        if not self.product_template_id or not self.course_id:
            self.get_academic_product_template_id()
            
        register_id = self.env['op.admission.register'].search([
            ('state', 'in', ['confirm', 'application','admission']),
            ('product_template_id', '=', product_template_id.id),
            ('period','=', period )
            ], limit=1 )
        
        if register_id:
            if register_id.state == 'confirm':
                register_id.start_application()            
                
        if not register_id:
            course_id = self.env['op.course'].search([('product_template_id', '=', product_template_id.id )], limit=1)
            _logger.info("\n###\n log 001 \n###")
            if course_id:
                register_id = self.env['op.admission.register'].create({
                    'course_id': course_id.id,
                    'name': str(period) +' '+course_id.name,
                    'min_count': 1,
                    'max_count':500,
                    'period': period,
                    'start_date':fields.Date.today(),
                    'end_date': self.gat_date_max_register(period),
                })
                register_id.start_application()
            else:
                msn = "No se encontro un Programa academico/Curso que este relacionado con el producto %s." % product_template_id.name
                self.error_admission_msn = msn if not self.error_admission_msn else self.error_admission_msn+'\n'+msn
                self.error_admission = True
                
        
        self.admission_register_id = register_id
        
      
    def action_get_admision_id(self):
        auto_ad = self.auto_ad_active()
        if auto_ad:
            if self.admission_register_id:
                self.get_admision_id(self.admission_register_id)
            
            
    def get_lot_id(self, course_id):
        date = self.admission_date #datetime.now()
        year = date.strftime("%y")
        month = date.strftime("%m")
        
        profix_01 = course_id.product_template_id.categ_id.code or ''
        prefix_02 = 'NF'
        #prefix_03 = 'IS'
        prefix_04 = month  #   Número del mes del año
        prefix_05 = year   #   últimos dígitos del año
        prefix_06 = {'es_MX': 'E', 'pt_BR': 'P'}.get(course_id.lang, '')     #   Digito del Idioma
        prefix_011 = course_id.code or ''
        
        
        # course_id.code+fields.Datetime.now().strftime('%Y%m%d%H%M%S')
        op_batch = self.env['op.batch']
        code = profix_01 + prefix_011 + prefix_02 +  prefix_04 + prefix_05 + prefix_06 #prefix_03 +
        
        lot_id = op_batch.search([('code','=',code)])
        
        
    
        if not lot_id:
            
            ad = self.env['auto.admission.required'].search([], limit=1)
        
            lot_values = {}
            if course_id.lang == 'es_MX':
                lot_values.update({
                    'tutor_id': ad.mx_tutor_id.id if ad.mx_tutor_id else False,
                    'professor_id': ad.mx_professor_id.id if ad.mx_professor_id else False,
                    'coordinator': ad.mx_coordinator.id if ad.mx_coordinator else False,
                    'teams_domain': ad.mx_teams_domain if ad.mx_teams_domain else False,
                    'teams_link': ad.mx_teams_link if ad.mx_teams_link else False,
                    'teams_msg': ad.mx_teams_msg if ad.mx_teams_msg else False,
                    'modality_id': ad.mx_modality_id.id if ad.mx_modality_id else False,
                })
            if course_id.lang == 'pt_BR':     
                lot_values.update({
                    'tutor_id': ad.br_tutor_id.id if ad.br_tutor_id else False,
                    'professor_id': ad.br_professor_id.id if ad.br_professor_id else False,
                    'coordinator': ad.br_coordinator.id if ad.br_coordinator else False,
                    'teams_domain': ad.br_teams_domain if ad.br_teams_domain else False,
                    'teams_link': ad.br_teams_link if ad.br_teams_link else False,
                    'teams_msg': ad.br_teams_msg if ad.br_teams_msg else False,
                    'modality_id': ad.br_modality_id.id if ad.br_modality_id else False,
                })
                
            lot_values.update({
                'name': code,
                'code': code,
                'course_id': course_id.id,
                'end_date': fields.Date.today() + relativedelta(years=1),
            })
            
            lot_id = op_batch.create(lot_values)
            
        return lot_id
        
    def get_admision_id(self,admission_register_id):        
        
        op_admission = self.env['op.admission']
        
        name = self.partner_id.name.replace('  ',' ').replace('   ',' ').replace('    ',' ').replace('     ',' ').replace('      ',' ').split(' ')
        
        first_name = '-'
        last_name = '-'
        if len(name)==1:
            first_name=name[0]
        if len(name)>1:
            first_name = ''
            for i in range(0,len(name)-1):
                first_name+=str(name[i])+' '
            last_name = name[-1]
        
        op_admission = op_admission.create({
            'name': self.partner_id.name,
            'first_name': first_name.strip(),
            'last_name': last_name.strip(),
            'sale_id': self.id,
            'email': self.partner_id.email,
            'mobile': self.partner_id.mobile,
            'phone':self.partner_id.phone,
            # 'product_template_id': self.product_template_id.id,
            'partner_id': self.partner_id.id,
            'register_id' : admission_register_id.id,
            'course_id' : admission_register_id.course_id.id,
            'application_date': fields.datetime.now(),
            'admission_date': fields.datetime.now(),
            'fees_term_id': self.env['op.fees.terms'].search([], limit=1).id,
            'gender': self.gender or self.partner_id.gender or 'o',
            'batch_id': self.get_lot_id(admission_register_id.course_id).id,
            'order_id': self.id,    
            
        })
        
        
        self.admission_id = op_admission.id
        
    
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for product in self.order_line:            

            if not product.product_template_id.course_type:
                raise UserError('Producto: %s \n\nRequerido "Modalidad": Especificar la modalidad del producto, contacte son el area de Contabilidad o Sistemas.' % (product.product_template_id.name) )
        
        return res


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'    
    """
    Enviar Solicitud de aplicacion desde Ventas.
    """
    admission_id = fields.Many2one('op.admission', string="Admisión" , copy=False) 
    elearning_id = fields.Many2one('slide.channel', string="eLearning" , copy=False) 
    elearning_partner_id = fields.Many2one('slide.channel.partner', string="eLearning Estudiante" , copy=False) 
    
    start_date_enroller = fields.Date(
        string='Fecha de inicio'
    )
    
    
    course_type = fields.Selection(
        string='Modalidad',
        related="product_id.course_type" ,
        selection=[('none', 'Ninguno'),('online', 'Online'), ('classroom', 'Online y Classroom')] ,
        )
    date_order = fields.Datetime(
        related="order_id.date_order",
        readonly=True,
        store=True,
        index=True,
    )
    account_analytic_id = fields.Many2one(
        related="order_id.analytic_account_id",
        readonly=True,
        store=True,
        index=True,
    )

    state_academic = fields.Selection(
        string='Estado de Solicitud',
        selection=[('waiting', 'En espera'),('process', 'En proceso'), ('done', 'Atendido')] ,
        tracking=True,
        default='waiting',
        copy=False
        )

    def state_academic_to_process(self):
        for self in self:
            self.state_academic = 'process'
    
    def state_academic_to_done(self):
        for self in self:
            self.state_academic = 'done'
    
    def state_academic_to_waiting(self):
        for self in self:
            self.state_academic = 'waiting'

    def elearning_add_user(self):
        for self in self:

            if self.course_type in ['classroom'] and not self.admission_id:
                    raise UserError('Primero debe generar la admision del Estudiante.' %  self.order_partner_id.name )                

            if self.course_type in ['classroom','online' ]:
                if not self.order_partner_id.country_id:
                    raise UserError('Cliente: %s \n\nRequerido "Pais": Especificar el pais dentro de la informacion de contacto.' %  self.order_partner_id.name )
                
                #elearning = self.env['slide.channel'].search([('product_template_id','=', product.product_template_id.id)], limit=1)
                #if not self.elearning_id:
                #    raise UserError('Producto: %s \n\nRequerido "Aperturar curso en Elearning (Campus)": Contacte con el departamento Academico.' % (self.product_template_id.name) )
                #else:                    
                #    self.env['slide.channel.partner'].search([('channel_id','=', self.elearning_id.id),('partner_id','=', self.partner_id.id)]).unlink()

                #    self.elearning_partner_id = self.env['slide.channel.partner'].create({
                #        'partner_id': self.order_partner_id.id,
                #        'channel_id': self.elearning_id.id,
                #        'partner_email': self.order_partner_id.email,
                #        'admission_id': self.admission_id.id,                        
                #   })



    def action_send_student(self):
        """op_admission = self.env['op.admission'].search([])
        action = self.env["ir.actions.actions"]._for_xml_id("openeducat_admission.view_op_admission_form")        
        # action['domain'] = [('id', 'in', op_admission.ids)]
        action['context'] = [()]
        action['context'] = {}
        action['target'] = 'new'
        action['flags'] = {'action_buttons': False}
        return action"""
        # raise UserError(str(self.order_partner_id.id))
        

        name = self.order_partner_id.name.replace('  ',' ').replace('   ',' ').replace('    ',' ').replace('     ',' ').replace('      ',' ').split(' ')
        
        first_name = ''
        middle_name = ''
        last_name = ''
        if len(name)==1:
            first_name=name[0]
        if len(name)>1:
            first_name = ''
            for i in range(0,len(name)-1):
                first_name+=str(name[i])+' '
            last_name = name[-1]
        
        
        return {
            #'name': self.order_id,
            'res_model': 'op.admission',
            'type': 'ir.actions.act_window',
            'context': {
                'default_first_name':first_name.strip(),
                'default_last_name':last_name.strip(),
                'default_sale_id':self.order_id.id,
                'default_email':self.order_id.partner_id.email,
                'default_mobile':self.order_id.partner_id.mobile,
                'default_phone':self.order_id.partner_id.phone,
                'default_product_template_id':self.product_template_id.id,
                'default_sale_line_id':self.id,
                'default_partner_id': self.order_partner_id.id,
                'default_order_id': self.order_id.id
            },
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': self.env.ref("openeducat_admission.view_op_admission_form").id,
            'target': 'new'
        }
            
    def action_open_admission_id(self):
        return {
            #'name': self.order_id,
            'res_model': 'op.admission',
            'type': 'ir.actions.act_window',
            'res_id': self.admission_id.id,
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': self.env.ref("openeducat_admission.view_op_admission_form").id,
            'target': 'target'
        }
        