import base64
from odoo import fields, http, _
from datetime import timedelta
from odoo.http import request
from werkzeug.exceptions import NotFound
from odoo.exceptions import ValidationError
from odoo.addons.web.controllers.binary import Binary
from odoo.addons.portal.controllers import portal
from odoo.addons.portal.controllers.portal import pager as portal_pager
from odoo.osv.expression import OR


class BinaryInh(Binary):

    @http.route('/web/content/<string:model>/<int:id>/<string:field>', type='http', auth="public")
    # pylint: disable=redefined-builtin,invalid-name
    def certificate_download(self, xmlid=None, model='ir.attachment', id=None, field='raw',
                       filename=None, filename_field='name', mimetype=None, unique=False,
                       download=False, access_token=None, nocache=False):
        attachment_id = False
        if model == 'ir.attachment':
            attachment_id = request.env[model].sudo().search([('id','=',id)])
        if attachment_id and attachment_id.certificado_web:
            user_id = request.env.user 
            student_id = request.env['op.student'].sudo().search([('user_id','=',user_id.id)], limit=1)
            certificate_log = request.env['certificate.log'].sudo()
            log_vals = {
                        'date':fields.Datetime.now(),
                        'certificate_name':attachment_id.name,
                        'download_from': 'web',
                        'user_id': request.env.user.id,
                        'student_id': student_id.id,
                        'invoice_id': attachment_id.cert_invoice_id.id
                       }
            certificate_log.create(log_vals)
        res = super().content_common(xmlid=xmlid, model=model, 
            id=id, field=field, filename=filename, filename_field=filename_field, 
            mimetype=mimetype, unique=unique, download=download, 
            access_token = access_token, nocache=nocache)
        return res




class CertificatesPortal(portal.CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        user = request.env.user
        student_id = request.env['op.student'].sudo().search([('user_id','=',user.id)])
        Attachment = request.env['ir.attachment'].sudo()
        student_attachment_ids = Attachment.search([('res_model','=','op.student'),('res_id','=',student_id.id)])
        if 'certificates_count' in counters:
            domain = []        
            domain += [('res_model', '=', 'op.student')]
            domain += [('id','in',student_attachment_ids.ids)]
            domain += [('certificado_web','=',True)]
            certificates_count = Attachment.sudo().search_count(domain) \
                if Attachment.sudo().check_access_rights('read', raise_exception=False) else 0
            values['certificates_count'] = certificates_count if certificates_count else '0'
        return values
    
    @http.route(['/verificar_documento'], type='http', auth="public", website=True, sitemap=False)
    def verificar_documento(self, **kw):
        if request.httprequest.method == 'GET':
            data = {}
            if kw and kw.keys():
                for val in kw.keys():
                    data[val] = kw.get(val)
            verified_values = request.env['op.sign_certificate'].sudo().web_verify_certificate(data)
            return request.render("isep_openeducat_reports.portal_verificar_documento", {'values':[verified_values]})
        return NotFound

    @http.route(['/my/certificates', '/my/certificates/page/<int:page>'], type='http', auth="user", website=True, sitemap=False)
    def portal_my_certificates(self, page=1, sortby=None, filterby=None, search=None, search_in='all', groupby='none', **kw):
        user = request.env.user
        new_invoice = False
        student_id = request.env['op.student'].sudo().search([('user_id','=',user.id)])

        try:
           cert_days_fpayment = int(http.request.env["ir.config_parameter"].sudo().get_param("cert_days_fpayment"))
        except ValueError:
           cert_days_fpayment = 7
        try:
           cert_days_fdownload = int(http.request.env["ir.config_parameter"].sudo().get_param("cert_days_fdownload"))
        except ValueError:
           cert_days_fdownload = 3



        if request.httprequest.method == 'POST':
            required_certificate = kw.get ('selection_value', False)
            required_batch = kw.get ('batch_value', False)
            if required_certificate:
                try:
                    required_certificate = int(required_certificate)
                except (ValueError, TypeError):
                    raise ValidationError("Valor Inválido")
                try:
                    required_batch = int(required_batch)
                except (ValueError, TypeError):
                    raise ValidationError("Valor Inválido")
 
                report_id = request.env['ir.actions.report'].sudo().search([('id', '=', required_certificate)])
                if not report_id:
                    raise ValidationError("Reporte Inválido")
                batch_id = request.env['op.batch'].sudo().search([('id', '=', required_batch)])
                if not batch_id:
                    raise ValidationError("Valor Inválido")
                
                student_course_ids = request.env['op.student.course'].sudo().search([('batch_id', '=', required_batch)])
                if batch_id not in student_course_ids.mapped('batch_id'):
                    raise ValidationError("Valor Inválido")
                #Check if certificate can be created
                access_res = report_id.check_web_available(student_id,batch_id)
                if access_res and type(access_res) == dict and 'error_message' in access_res.keys():
                    values = {'error_message': access_res.get('error_message')}
                    return request.render("isep_openeducat_reports.error_template_message", values)
                if not report_id.certificado_gratuito:
                    invoice_id = False
                    xmlids = report_id.get_external_id()
                    report_xml_id = xmlids.get(report_id.id)

                    if report_xml_id == 'isep_openeducat_reports.r_certificado7': #Título
                        #Buscar factura de título
                        subscription_data = student_id.sudo().get_subscription_data()
                        sale_order_ids = subscription_data.get('sale_order_ids', False)
                        for line in sale_order_ids.mapped('subscription_schedule.invoice_ids.invoice_line_ids'):
                            if line.product_id.is_title and line.move_id.payment_state in ['paid','in_payment']:
                                certificates = request.env['ir.attachment'].sudo().search([('cert_invoice_id','=',line.move_id.id)])
                                if not certificates: # Que la factura no esté amparando otro certificado.
                                    invoice_id = line.move_id
                                    break
                        if invoice_id:
                        #Se encontró una factura por título
                            invoice_id.certificado_web = True #Aparecer la factura en web
                            new_invoice = invoice_id
                        
                    if not invoice_id:  
                        #Generar Factura
                        certificate_product_id = request.env.company.cert_product_id.sudo()
                        invoice_line_vals={
                            'product_id':certificate_product_id.id,
                            'quantity':1.0,
                            'name': '%s. Certificado %s' %(certificate_product_id.display_name,report_id.name),
                            'price_unit': report_id.list_price or certificate_product_id.list_price,
                            }
    
                        invoice_vals={
                            'partner_id': user.partner_id.id,
                            'certificado_web': True,
                            'move_type': 'out_invoice',
                            'company_id': request.env.company.id,
                            'invoice_date': fields.Datetime.now(),
                            'invoice_date_due': fields.Datetime.now()+ timedelta(days=cert_days_fpayment),
                            'invoice_line_ids': [(0,0,invoice_line_vals)]
                            }
                        new_invoice = request.env['account.move'].sudo().create(invoice_vals)
                        if not new_invoice:
                            raise ValidationError('No se pudo solicitar el Certificado')
                        new_invoice.action_post() 
                #Generar PDF
                data = {
                     'admissions': student_course_ids,
                     'batch_id': batch_id.sudo().id,
                     'student_ids': student_id.ids,
                     'doc_model': 'op.student',  # Odoo model name you're working with
                }
                pdf, tipo = report_id.sudo().with_context(disable_attachment=True)._render_qweb_pdf(report_id.xml_id, data=data)
                pdf_content = base64.b64encode(pdf)
                #Generar Attachment
                attach = request.env['ir.attachment'].sudo().create({
                    'name': report_id.name,
                    'type': 'binary',
                    'datas': pdf_content,
                    'store_fname': report_id.name + '.pdf',
                    'res_model': student_id._name,
                    'res_id': student_id.id,
                    'cert_invoice_id': new_invoice and new_invoice.id or False,
                    'certificado_web': True,
                    'certificado_gratuito': report_id.certificado_gratuito,
                    'mimetype': 'application/pdf'
                })

                
                #Generar Enlace de Pago
                #Redirigir a Enlace de Pago        
            return request.redirect('/my/certificates')

        values = self._prepare_portal_layout_values()
        Attachment = request.env['ir.attachment'].sudo()
        student_attachment_ids = Attachment.search([('res_model','=','op.student'),('res_id','=',student_id.id)])
        domain = [
            ('res_model', '=', 'op.student'),
            ('id','in',student_attachment_ids.ids),
            ('certificado_web','=',True)
            ]        
        
        
        searchbar_sortings = {
            'date': {'label': _('Nuevo'), 'order': 'id desc'},
            'name': {'label': _('Nombre'), 'order': 'name asc, id asc'},
        }
        
        # default sortby order
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']
        
        
        searchbar_inputs = {
            'all': {'input': 'all', 'label': _('Buscar en todo')},
            'name': {'input': 'name', 'label': _('Buscar en nombre')},
            'description': {'input': 'description', 'label': _('Buscar en descripción')},
        }
        
        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
        }
        
        # search
        if search and search_in:
            search_domain = []
            if search_in in ('name', 'all'):
                search_domain = OR([search_domain, [('name', 'ilike', search)]])
            if search_in in ('description', 'all'):
                search_domain = OR([search_domain, [('description', 'ilike', search)]])            
            domain += search_domain
    
        # count for pager
        certificates_count = Attachment.search_count(domain)
        
        # default filter by value
        if not filterby:
            filterby = 'all'
        
        # make pager
        pager = portal_pager(
            url="/my/certificates",
            url_args={'sortby': sortby, 'filterby': filterby, 'groupby': groupby, 'search_in': search_in, 'search': search},
            total=certificates_count,
            page=page,
            step=self._items_per_page
        )
        
        # search the certificates to display, according to the pager data
        certificates = Attachment.search(
            domain,
            order=order,
            limit=self._items_per_page,
            offset=pager['offset']
        )
        
        grouped_certificates = []
        if certificates:
            grouped_certificates = [certificates]
        
        
        request.session['my_certificates_history'] = certificates.ids[:100]
        certificate_ids = http.request.env['ir.actions.report'].sudo().search([('model','ilike','%op.student%'),('certificado_web','=',True)])
        batch_ids = request.env['op.student.course'].sudo().search([('student_id','=',student_id.id)]).mapped('batch_id')
        values.update({
            'certificate_ids': certificate_ids.sudo(),
            'batch_ids': batch_ids.sudo(),
            'certificates': certificates.sudo(),
            'grouped_certificates': grouped_certificates,
            'page_name': 'Certificados',
            'default_url': '/my/certificates',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'search': search,
            'sortby': sortby,
            'groupby': groupby,
            'filterby': filterby,                        
            'cert_days_fpayment': cert_days_fpayment,
            'cert_days_fdownload': cert_days_fdownload,
            'base_url': http.request.env["ir.config_parameter"].sudo().get_param("web.base.url"),
        })
        return request.render("isep_openeducat_reports.portal_my_certificates", values)
        
    
    @http.route(['/new_payment_link/<int:attachment>'], type='http', auth="user", website=True, sitemap=False)
    def new_payment_link(self, **kw):
        att_id = kw.get('attachment', False)
        if att_id:
            user = request.env.user
            student_id = request.env['op.student'].sudo().search([('user_id','=',user.id)])
            attachment_id = request.env['ir.attachment'].sudo().search([('id','=',int(att_id))], limit = 1)
            if attachment_id.res_id == student_id.id and attachment_id.cert_invoice_id and attachment_id.cert_invoice_id.payment_state != 'paid':
                payment_link_id = request.env['payment.link.wizard'].sudo().with_context(active_model = 'account.move', active_id = attachment_id.cert_invoice_id.id).create({})
                if payment_link_id and payment_link_id.link :
                    return request.redirect(payment_link_id.link)
        return request.redirect('/my/certificates')
