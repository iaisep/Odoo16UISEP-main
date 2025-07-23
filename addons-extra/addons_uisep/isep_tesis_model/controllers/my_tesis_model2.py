# -*- coding: utf-8 -*-
import base64
import logging


from odoo import http
from odoo.http import request
import base64
import io
from werkzeug.utils import redirect
from odoo.tools import json
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.portal.controllers import portal

_logger = logging.getLogger(__name__)
class preparteTesisReviewPortal(portal.CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        # _logger.info('_prepare_home_portal_values',counters)

        if not 'tesis_models_count' in counters:
            counters.append('tesis_models_count')

        values = super()._prepare_home_portal_values(counters)
        if 'tesis_models_count' in counters:
            values['tesis_models_count'] = request.env['tesis.model'].sudo().search_count([
                ('create_uid', '=', request.env.user.id)
            ])
            if values['tesis_models_count']==0:
                values['tesis_models_count']="Nuevo"



        return values

class TesisReviewPortal(http.Controller):


    @http.route(['/my/tesis_models2'], type='http', auth='user', website=True, csrf=False)
    def list_tesis_models(self, **kwargs):
        """
        Página para listar las solicitudes del usuario autenticado.
        """
        user = request.env.user
        # Filtrar solicitudes del usuario actual
        tesis_models = request.env['tesis.model'].sudo().search([
            ('create_uid', '=', user.id)
        ])

        values={'tesis_models':tesis_models}

        return request.render('isep_tesis_model.tesis_model_portal_template', values)


    @http.route(['/my/tesis_models2/accept'], type='http', auth='user', methods=['POST'], csrf=False)
    def accept_tesis_model(self, **kwargs):
        request_id = int(kwargs.get('request_id'))
        tesis_model = request.env['tesis.model'].sudo().browse(request_id)

        if tesis_model and tesis_model.create_uid.id == request.env.user.id:
            tesis_model.sudo().write({'state': 'approved'})
            return request.redirect('/my/tesis_models2')

    @http.route(['/my/tesis_models2/decline'], type='http', auth='user', methods=['POST'], csrf=True)
    def decline_tesis_model(self, **kwargs):
        request_id = int(kwargs.get('request_id'))
        tesis_model = request.env['tesis.model'].sudo().browse(request_id)

        if tesis_model and tesis_model.create_uid.id == request.env.user.id:
            tesis_model.sudo().write({'state': 'rejected'})
            return request.redirect('/my/tesis_models2')


    @http.route(['/my/tesis_model/<int:request_id>'], type='http', auth="user", website=True)
    def tesis_model_details(self, request_id, **kwargs):
        tesis_model = request.env['tesis.model'].sudo().browse(request_id)
        if not tesis_model.exists():
            return request.not_found()

        return request.render('isep_tesis_model.tesis_model_portal_details_template', {
            'tesis_model': tesis_model,
        })

    @http.route('/web/submit_documenttr', type='http', auth='user', website=True, csrf=False)
    def submit_documenttr(self, **kwargs):
        tesis_model_id = int(kwargs.get('tesis_model_id'))

        file = kwargs.get('file')  # Este es el objeto FileStorage
        document_name = file.filename
        description = kwargs.get('description')
        #status_thesis = kwargs.get('status_thesis')

        # Verificar que el archivo está presente
        if file:
            file_content = file.read()  # Convertir el archivo a bytes

            # Codificar el contenido en base64 (Odoo requiere este formato para los campos Binary)
            file_content_base64 = base64.b64encode(file_content)

            # Obtenemos la solicitud de práctica
            tesis_model = request.env['tesis.model'].sudo().browse(tesis_model_id)

            # Crear un nuevo documento asociado a la solicitud de práctica
            values={
                'name': document_name,
                'datas': file_content_base64,  # Guardar el archivo en base64
                'description': description,
                'res_model':'tesis.model',
                'tesis_model_id': tesis_model_id,
                'res_id': tesis_model_id,
                'status_thesis': tesis_model.status_thesis,
            }

            values.update({
                'datas': file_content_base64,  # Guardar el archivo en base64
            })

            xya=tesis_model.env['ir.attachment'].sudo().create(values)
            sql="""insert into tesis_model_documents(res_id,tesis_model_id)
                select id,res_id from ir_attachment
                where res_model='tesis.model' and id not in (
                select res_id from tesis_model_documents)"""
            request.env.cr.execute(sql)

        # Redirigir al usuario a la página de detalles de la solicitud
        return request.redirect('/my/tesis_model/%s' % tesis_model.id)

    @http.route(['/my/notificacionestr/download/<string:attachment_id>', ],  auth='public')
    def download_attachment(self, attachment_id):
        dominio=[
            ('res_model', '=', 'tesis.model'),
            ('id', '=', int(attachment_id))]

        attachment = request.env['ir.attachment'].sudo().search(dominio)

        if attachment:
            attachment = attachment[0]

        else:
            return redirect('/web/content')

        if attachment["type"] == "url":

            if attachment["url"]:
                return redirect(attachment["url"])
            else:
                return request.not_found()
        elif attachment["datas"]:

            data = io.BytesIO(base64.standard_b64decode(attachment["datas"]))
            return http.send_file(data, filename=attachment['name'], as_attachment=True)
            # return odoo.http.Stream(data, filename=attachment['name'], as_attachment=True)
        else:
            return request.not_found()

    @http.route(['/my/notificacionestr/borrar/<string:attachment_id>/<string:tesis_model_id>', ], auth='public')
    def borrar_attachment(self, attachment_id,tesis_model_id ):
        dominio = [
            ('res_model', '=', 'tesis.model'),
            ('id', '=', int(attachment_id))]
        attachment_id=request.env['ir.attachment'].sudo().search(dominio)
        r=attachment_id.unlink()
        return request.redirect('/my/tesis_model/%s' % tesis_model_id)
    
    @http.route(['/my/notificacionestr/comment/<int:attachment_id>'], type='http', auth='user', website=True)
    def view_attachment_comment(self, attachment_id, **kwargs):
        attachment = request.env['ir.attachment'].sudo().browse(attachment_id)
        if not attachment.exists():
            return request.not_found()
        return request.render('isep_tesis_model.tesis_attachment_comment_template', {
            'attachment': attachment,
        })
