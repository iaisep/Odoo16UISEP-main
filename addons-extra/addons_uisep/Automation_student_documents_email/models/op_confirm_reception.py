# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
import pytz
from datetime import datetime
from dateutil.relativedelta import relativedelta
_logger = logging.getLogger(__name__)
from datetime import datetime

class ResPartnerOP(models.Model):

	_inherit = 'res.partner'  

	have_documents = fields.Boolean(string='Documentos Obtenidos',help='Marcar si completo los documentos')

	official_title = fields.Boolean(string='Titulo oficial',help='Marcar si el custo cuenta con Titulo oficial',invisible=True)

	date_time_next = fields.Date(string='Fecha ', help='Fecha automatica', invisible=True)

	text_missing = fields.Html(string='Falta', help='Documentos faltantes')	

	email_send_status=fields.Selection(string='Correo Enviado', selection=[('1','1 Mes'),('2', '2 Mes'),('3', '3 Mes'), ('4', '4 Mes'),('5', '5 Mes'),('6','Recolectados'),('7','Ultima')],default='1')
  
	
	def documens_missing(self):		
		for user in self.env['res.partner'].search([]):			
			if user.official_title:
				result = self.env['ir.attachment'].search([('partner_id','=',user.id)])						
				if result:					
					resultfilter=result.filtered(lambda r: r.state != 'accepted').sorted(key=lambda r: r.name)					
					user.text_missing = ''					
					lista='<ol>'
					for item in resultfilter.mapped('document'):
						_logger.info('item %s', item)
						lista = lista +'<li>'+  item+ '</li>'
					lista = lista + '</ol>'		
					_logger.info('lista %s', lista)
					user.text_missing = lista		
	

	def update_date_time_next(self):		
		users = self.env['res.partner'].search([])			
		for user in users:	
			user_tz = pytz.timezone(user.tz or 'UTC')
			_logger.info('user_tz %s', user_tz)			
			now=datetime.now(user_tz)
			next_month=now + relativedelta(months=1)			
			user.date_time_next = next_month
	

	def send_email(self):
		data=self.env['res.partner'].search([('official_title','=',True)])
		_logger.info('INICIA ACTUALIZACION')
		self.documens_missing()
		self.update_date_time_next()
		_logger.info('FINALIZA ACTUALIZACION')
		
		for user in data:
			ctx = {
			'lang': user.lang,
	     	}	
			if user.email_send_status == '1' and not user.have_documents:
				template={
					'en_US': 'Automation_student_documents_email.automatic_students_document_success_email_months1_en',
					'pt_BR': 'Automation_student_documents_email.automatic_students_document_success_email_months1_pt_br',
					'es_ES': 'Automation_student_documents_email.automatic_students_document_success_email_months1',
				}
				template_ref = template.get(user.lang, 'Automation_student_documents_email.automatic_students_document_success_email_months1')
				self.env.ref(template_ref).with_context(ctx).send_mail(user.id,force_send=True)		
				user.email_send_status='2'
			elif user.email_send_status == '2' and not user.have_documents:
				template={
					'en_US': 'Automation_student_documents_email.automatic_studens_document_success_email_months2_en',
					'pt_BR': 'Automation_student_documents_email.automatic_studens_document_success_email_months2_pt_br',
					'es_ES': 'Automation_student_documents_email.automatic_studens_document_success_email_months2',
				}
				template_ref = template.get(user.lang, 'Automation_student_documents_email.automatic_studens_document_success_email_months2')
				self.env.ref(template_ref).with_context(ctx).send_mail(user.id,force_send=True)	
				user.email_send_status='3'
			elif user.email_send_status == '3' and not user.have_documents:
				template={
					'en_US': 'Automation_student_documents_email.automatic_studens_document_success_email_months3_en',
					'pt_BR': 'Automation_student_documents_email.automatic_studens_document_success_email_months3_pt_br',
					'es_ES': 'Automation_student_documents_email.automatic_studens_document_success_email_months3',
				}
				template_ref = template.get(user.lang, 'Automation_student_documents_email.automatic_studens_document_success_email_months3')
				self.env.ref(template_ref).with_context(ctx).send_mail(user.id,force_send=True)	
				user.email_send_status='4'
			elif user.email_send_status == '4' and not user.have_documents:
				template={
					'en_US': 'Automation_student_documents_email.automatic_studens_document_success_email_months4_en',
					'pt_BR': 'Automation_student_documents_email.automatic_studens_document_success_email_months4_pt_br',
					'es_ES': 'Automation_student_documents_email.automatic_studens_document_success_email_months4',
				}
				template_ref = template.get(user.lang, 'Automation_student_documents_email.automatic_studens_document_success_email_months4')
				self.env.ref(template_ref).with_context(ctx).send_mail(user.id,force_send=True)	
				user.email_send_status='5'
			elif user.email_send_status == '5' and not user.have_documents:
				template={
					'en_US': 'Automation_student_documents_email.automatic_studens_document_success_email_months5_en',
					'pt_BR': 'Automation_student_documents_email.automatic_studens_document_success_email_months5_pt_br',
					'es_ES': 'Automation_student_documents_email.automatic_studens_document_success_email_months5',
				}
				template_ref = template.get(user.lang, 'Automation_student_documents_email.automatic_studens_document_success_email_months5')
				self.env.ref(template_ref).with_context(ctx).send_mail(user.id,force_send=True)	
				user.email_send_status='7'			
			elif user.have_documents and user.email_send_status != '6':
				template={
					'en_US': 'Automation_student_documents_email.automatic_studens_document_success_email_en',
					'pt_BR': 'Automation_student_documents_email.automatic_studens_document_success_email_pt_br',
					'es_ES': 'Automation_student_documents_email.automatic_studens_document_success_email',
				}
				template_ref = template.get(user.lang, 'Automation_student_documents_email.automatic_studens_document_success_email')
				self.env.ref(template_ref).with_context(ctx).send_mail(user.id,force_send=True)
				user.email_send_status='6'
			_logger.info('user.email_send_status %s', user.email_send_status)
			
    


	
 