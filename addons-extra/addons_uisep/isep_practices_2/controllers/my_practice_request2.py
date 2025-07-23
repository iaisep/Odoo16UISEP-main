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
class AsignacionesPortal(portal.CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        # _logger.info('_prepare_home_portal_values',counters)

        if not 'practice_requests_count' in counters:
            counters.append('practice_requests_count')

        values = super()._prepare_home_portal_values(counters)
        if 'practice_requests_count' in counters:
            values['practice_requests_count'] = request.env['practice.request'].sudo().search_count([
                # ('create_uid', '=', request.env.user.id)
                ('email', '=', request.env.user.email)
            ])
            if values['practice_requests_count']==0:
                values['practice_requests_count']="Nuevo"



        return values

class PracticeCenterPortal(http.Controller):


    @http.route(['/my/practice_requests2'], type='http', auth='user', website=True, csrf=False)
    def list_practice_requests(self, **kwargs):
        """
        Página para listar las solicitudes del usuario autenticado.
        """
        user = request.env.user
        # Filtrar solicitudes del usuario actual
        practice_requests = request.env['practice.request'].sudo().search([
            # ('create_uid', '=', user.id)
            ('user_id', '=', user.id)
        ])

        values={'practice_requests':practice_requests}

        return request.render('isep_practices_2.practice_request_portal_template', values)


    @http.route(['/my/practice_requests2/accept'], type='http', auth='user', methods=['POST'], csrf=False)
    def accept_practice_request(self, **kwargs):
        request_id = int(kwargs.get('request_id'))
        practice_request = request.env['practice.request'].sudo().browse(request_id)

        if practice_request and practice_request.create_uid.id == request.env.user.id:
            practice_request.sudo().write({'state': 'approved'})
            return request.redirect('/my/practice_requests2')

    @http.route(['/my/practice_requests2/decline'], type='http', auth='user', methods=['POST'], csrf=True)
    def decline_practice_request(self, **kwargs):
        request_id = int(kwargs.get('request_id'))
        practice_request = request.env['practice.request'].sudo().browse(request_id)

        if practice_request and practice_request.create_uid.id == request.env.user.id:
            practice_request.sudo().write({'state': 'rejected'})
            return request.redirect('/my/practice_requests2')


    @http.route(['/my/practice_request/<int:request_id>'], type='http', auth="user", website=True)
    def practice_request_details(self, request_id, **kwargs):
        practice_request = request.env['practice.request'].sudo().browse(request_id)
        if not practice_request.exists():
            return request.not_found()

        return request.render('isep_practices_2.practice_request_portal_details_template', {
            'practice_request': practice_request,
        })

    @http.route('/web/submit_document', type='http', auth='user', website=True, csrf=False)
    def submit_document(self, **kwargs):
        try:
            practice_request_id = int(kwargs.get('practice_request_id', 0))

            # Verificar que practice_request_id existe en la BD
            practice_request = request.env['practice.request'].sudo().browse(practice_request_id)
            if not practice_request.exists():
                return request.redirect('/my/practice_requests?error=invalid_request')

            file = kwargs.get('file')
            if not file:
                return request.redirect('/my/practice_requests?error=no_file')

            document_name = file.filename
            description = kwargs.get('description')
            document_type = kwargs.get('document_type')

            file_content = file.read()
            file_content_base64 = base64.b64encode(file_content)

            values = {
                'name': document_name,
                'datas': file_content_base64,
                'description': description,
                'res_model': 'practice.request',
                'res_id': practice_request_id,
                'document_type': document_type,
            }

            attachment = request.env['ir.attachment'].sudo().create(values)

            # Asegurar que solo se inserten registros válidos en practice_request_documents
            sql = """
                INSERT INTO practice_request_documents (res_id, practice_request_id)
                SELECT id, res_id FROM ir_attachment
                WHERE res_model='practice.request'
                AND id NOT IN (SELECT res_id FROM practice_request_documents)
                AND res_id IN (SELECT id FROM practice_request);
            """
            request.env.cr.execute(sql)

            return request.redirect('/my/practice_request/%s' % practice_request.id)

        except Exception as e:
            return request.redirect('/my/practice_requests?error=server_error')


        # practice_request_id = int(kwargs.get('practice_request_id'))

        # file = kwargs.get('file')  # Este es el objeto FileStorage
        # document_name = file.filename
        # description = kwargs.get('description')
        # document_type = kwargs.get('document_type')

        # # Verificar que el archivo está presente
        # if file:
        #     file_content = file.read()  # Convertir el archivo a bytes

        #     # Codificar el contenido en base64 (Odoo requiere este formato para los campos Binary)
        #     file_content_base64 = base64.b64encode(file_content)

        #     # Obtenemos la solicitud de práctica
        #     practice_request = request.env['practice.request'].browse(practice_request_id)

        #     # Crear un nuevo documento asociado a la solicitud de práctica
        #     values={
        #         'name': document_name,
        #         'datas': file_content_base64,  # Guardar el archivo en base64
        #         'description': description,
        #         'res_model':'practice.request',
        #         'practice_request_id': practice_request_id,
        #         'res_id': practice_request_id,
        #         'document_type':document_type,
        #     }

        #     values.update({
        #         'datas': file_content_base64,  # Guardar el archivo en base64
        #     })

        #     xya=practice_request.env['ir.attachment'].sudo().create(values)
        #     sql="""insert into practice_request_documents(res_id,practice_request_id)
        #         select id,res_id from ir_attachment
        #         where res_model='practice.request' and id not in (
        #         select res_id from practice_request_documents)"""
        #     request.env.cr.execute(sql)

        # # Redirigir al usuario a la página de detalles de la solicitud
        # return request.redirect('/my/practice_request/%s' % practice_request.id)

    @http.route(['/my/notificaciones/download/<string:attachment_id>', ],  auth='public')
    def download_attachment(self, attachment_id):
        dominio=[
            ('res_model', '=', 'practice.request'),
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

    @http.route(['/my/notificaciones/borrar/<string:attachment_id>/<string:practice_request_id>', ], auth='public')
    def borrar_attachment(self, attachment_id,practice_request_id ):
        try:
            # Buscar el adjunto en ir.attachment
            attachment = request.env['ir.attachment'].sudo().search([
                ('id', '=', int(attachment_id)),  # Asegurar que sea entero
                ('res_model', '=', 'practice.request')
            ], limit=1)

            if not attachment:
                # _logger.warning(f"No se encontró el adjunto con ID {attachment_id}.")
                return request.redirect('/my/practice_requests?error=not_found')

            # Si `practice_request_id` es None o 'False', lo obtenemos desde `attachment.res_id`
            if not practice_request_id or practice_request_id == "False":
                practice_request_id = str(attachment.res_id) if attachment.res_id else None
                # _logger.info(f"Se obtuvo el practice_request_id {practice_request_id} desde ir.attachment.")

            # Si sigue siendo None, hay un problema con los datos
            if not practice_request_id or practice_request_id == "False":
                # _logger.error(f"El adjunto {attachment_id} no tiene un res_id válido. No se puede redirigir correctamente.")
                return request.redirect('/my/practice_requests?error=invalid_request_id')

            # Eliminar el adjunto
            # _logger.info(f"Eliminando adjunto ID {attachment_id} de practice_request {practice_request_id}")
            attachment.unlink()

            # Redirigir correctamente
            return request.redirect(f'/my/practice_request/{practice_request_id}')

        except Exception as e:
            # _logger.error(f"Error eliminando el adjunto {attachment_id}: {str(e)}")
            return request.redirect('/my/practice_requests?error=delete_failed')


        # dominio = [
        #     ('res_model', '=', 'practice.request'),
        #     ('id', '=', int(attachment_id))]
        # attachment_id=request.env['ir.attachment'].sudo().search(dominio)
        # r=attachment_id.unlink()
        # return request.redirect('/my/practice_request/%s' % practice_request_id)
