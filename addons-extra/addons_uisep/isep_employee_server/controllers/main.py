from odoo import http
from odoo.http import request


class MainPdf(http.Controller):


    @http.route('/descargar_contrato_freelance/pdf', type='http', auth='public', website=True)
    def descargar_contrato_pdf(self, **kw):
        pdf_path = '/isep_employee_server/static/docs/FORMATO_CONTRATO_FREELANCE.pdf'
        return request.redirect(pdf_path)


    @http.route('/descargar_reglamento_interno/pdf', type='http', auth='public', website=True)
    def descargar_reglamento_pdf(self, **kw):
        pdf_path = '/isep_employee_server/static/docs/ISEP_Reglamento_Interno_Trabajo_actualizado.pdf'
        return request.redirect(pdf_path)


    @http.route('/descargar_proteccion_datos/pdf', type='http', auth='public', website=True)
    def descargar_proteccion_pdf(self, **kw):
        pdf_path = '/isep_employee_server/static/docs/Proteccion_Datos_Mexico_Comunicado.pdf'
        return request.redirect(pdf_path)