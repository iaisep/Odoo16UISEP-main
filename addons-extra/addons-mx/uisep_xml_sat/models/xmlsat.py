# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta, date
from cfdiclient import SolicitaDescarga, Fiel, Autenticacion, VerificaSolicitudDescarga, DescargaMasiva
import base64
from io import BytesIO
import zipfile
import logging
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement
_logger = logging.getLogger(__name__)


class XmlSatSolicitud(models.Model):
    _name = 'xmlsat.solicitud'
    _description = 'Solicitud de descarga'
    _order = 'id desc'
    _rec_name = 'id'

    @api.depends('id_solicitud')
    def name_get(self):
        result = []
        for solicitud in self:
            name = solicitud.id_solicitud
            result.append((solicitud.id, name))
        return result

    token = fields.Char('Token')
    rfc_solicitante = fields.Char('RFC solicitante', required=True)
    fecha_inicial = fields.Date('Fecha inicial', default=date.today() - timedelta(days = 1), required=True)
    fecha_final = fields.Date('Fecha final', default=date.today(), required=True)
    rfc_emisor = fields.Char('RFC emisor')
    rfc_receptor = fields.Char('RFC receptor',required=True)
    
    id_solicitud = fields.Char('Id solicitud')
    cod_estatus = fields.Char('Codigo estatus')
    mensaje = fields.Char('Mensaje')

    estado_solicitud = fields.Char('Estado solicitud')
    codigo_estado_solicitud = fields.Char('Codigo estado solicitud')
    numero_cfdis = fields.Char('Numero cfdis')
    paquetes = fields.One2many('xmlsat.paquete', 'solicitud', 'Paquetes')
    cfdis = fields.One2many('xmlsat.cfdi', 'solicitud', 'CFDIs')

    estatus = fields.Selection([('nueva', 'Nueva'), ('solicitar', 'Solicitar'), ('verificar', 'Verificar'), ('descargar', 'Descargar'), ('finalizado', 'Finalizado')],
        'Estatus', default="nueva")

    @api.model
    def default_get(self, fields):
        res = super(XmlSatSolicitud, self).default_get(fields)
        company = self.env.user.company_id
        res['rfc_solicitante'] = company.rfc
        res['rfc_receptor'] = company.rfc
        return res
    
    def regresar(self):
        for item in self:
            item.estatus = str(int(item.estatus) - 1) if int(item.estatus) > 1 else item.estatus
            
    def validar_requisitos(self):
        company = self.env.user.company_id
        if not company.fiel_password or not company.fiel_cer or not company.fiel_key:
            raise models.ValidationError('Primero debe proporcionar la FIEL en la configuración de la empresa')


    def get_token(self):
        self.validar_requisitos()
        company = self.env.user.company_id
        FIEL_PAS = company.fiel_password
        _logger.info('Get token, FIEL_PAS: ---------------> %s' % FIEL_PAS)
        cer_der = base64.b64decode(company.fiel_cer)
        key_der = base64.b64decode(company.fiel_key)
        fiel = Fiel(cer_der, key_der, FIEL_PAS)
        _logger.info('Get token, fiel: ---------------> %s' % fiel)
        auth = Autenticacion(fiel)
        return auth.obtener_token()

    def autenticar(self):
        self.token = self.get_token()
        _logger.info('Autenticar, token: ---------------> %s' % self.token)

    def solicitar_descarga(self):
        company = self.env.user.company_id
        FIEL_PAS = company.fiel_password
        cer_der = base64.b64decode(company.fiel_cer)
        key_der = base64.b64decode(company.fiel_key)
        fiel = Fiel(cer_der, key_der, FIEL_PAS)
        descarga = SolicitaDescarga(fiel)
        _logger.info('Solicitar descarga: ---------------> %s' % descarga)
        result = descarga.solicitar_descarga(self.token, self.rfc_solicitante, self.fecha_inicial, self.fecha_final, rfc_emisor=self.rfc_emisor or '', rfc_receptor=self.rfc_receptor or '')
        _logger.info('Solicitar result: ---------------> %s' % result)
        self.id_solicitud = result.get('id_solicitud','')
        _logger.info('Solicitar id_solicitud: ---------------> %s' % result.get('id_solicitud',''))
        self.cod_estatus = result.get('cod_estatus','')
        _logger.info('Solicitar cod_estatus: ---------------> %s' % result.get('cod_estatus',''))
        self.mensaje = result.get('mensaje', '')
        _logger.info('Solicitar mensaje: ---------------> %s' % result.get('mensaje',''))
        # Validar cod_estatus si tiene error
        if self.cod_estatus == '5000':
            self.estatus = 'verificar'
        # Validar cod_estatus si tiene error
        elif result.get('cod_estatus','') == '305':
            self.cod_estatus = result.get('cod_estatus','')
            self.mensaje = result.get('mensaje', '')
    
    def solicitar(self):
        self.autenticar()
        _logger.info('Solicitar, Procesando "F-autenticar": --------------->')
        self.solicitar_descarga()
        _logger.info('Solicitar, Procesando "F-solicitar_descarga": --------------->')

    def verificar_solicitud(self):
        company = self.env.user.company_id
        FIEL_PAS = company.fiel_password
        cer_der = base64.b64decode(company.fiel_cer)
        key_der = base64.b64decode(company.fiel_key)
        fiel = Fiel(cer_der, key_der, FIEL_PAS)
        v_descarga = VerificaSolicitudDescarga(fiel)
        _logger.info('Verificar solicitud, v_descarga: ---------------> %s' % (v_descarga))
        result = v_descarga.verificar_descarga(self.token, self.rfc_solicitante, self.id_solicitud)
        _logger.info('Verificar solicitud, result: ---------------> %s' % (result))
        self.cod_estatus = result.get('cod_estatus','')
        _logger.info('Verificar solicitud, cod_estatus: ---------------> %s' % result.get('cod_estatus',''))
        self.mensaje = result.get('mensaje', '')
        _logger.info('Verificar solicitud, mensaje: ---------------> %s' % result.get('mensaje',''))
        self.estado_solicitud = result.get('estado_solicitud', '')
        _logger.info('Verificar solicitud, estado_solicitud: ---------------> %s' % result.get('estado_solicitud',''))
        self.codigo_estado_solicitud = result.get('codigo_estado_solicitud', '')
        _logger.info('Verificar solicitud, codigo_estado_solicitud: ---------------> %s' % result.get('codigo_estado_solicitud',''))
        self.numero_cfdis = result.get('numero_cfdis', '')
        _logger.info('Verificar solicitud, numero_cfdis: ---------------> %s' % result.get('numero_cfdis',''))
        _logger.info('Verificar solicitud, paquetes: ---------------> %s' % result.get('paquetes', []))
        for paquete in result.get('paquetes', []):
            self.env['xmlsat.paquete'].create({'id_paquete': paquete, 'solicitud': self.id})
            _logger.info('Verificar solicitud, for paquete: ---------------> %s' % (paquete))
            _logger.info('Verificar solicitud, se crea registro para adjuntar descarga: --------------->')
        # Validar estado_solicitud si tiene error 'cod_estatus' != '5000'
        if self.estado_solicitud == 'verificar' and self.codigo_estado_solicitud =='5000':
            self.estatus = 'descargar'
            _logger.info('Verificar solicitud, cambio de estado Verificar a Descargar: --------------->')
        elif self.codigo_estado_solicitud == '5004':
            self.mensaje = 'No se encontró la solicitud'
            # break
    
    def verificar(self):
        self.autenticar()
        _logger.info('Verificar, Procesando "F-autenticar": --------------->')
        self.verificar_solicitud()
        _logger.info('Verificar, Procesando "F-verificar_solicitud": --------------->')
        if self.codigo_estado_solicitud == '5000':
            _logger.info('Verificar, Procesando "F-descagar_paquetes": --------------->')
            self.descargar_paquetes()

    def descargar_paquetes(self):
        company = self.env.user.company_id
        FIEL_PAS = company.fiel_password
        cer_der = base64.b64decode(company.fiel_cer)
        key_der = base64.b64decode(company.fiel_key)
        fiel = Fiel(cer_der, key_der, FIEL_PAS)
        descarga = DescargaMasiva(fiel)
        _logger.info('Descargar paquetes, descarga: ---------------> %s' % (descarga))
        # raise ValidationError(_("descargar_paquetes %s")%(descarga))
        for paquete in self.paquetes:
            result = descarga.descargar_paquete(self.token, self.rfc_solicitante, paquete.id_paquete)
            _logger.info('Descargar paquetes, result: ---------------> %s' % result)
            # self.cod_estatus = result.get('cod_estatus','')
            # self.mensaje = result.get('mensaje', '')
            # self.estatus = 'descargar'
            # if result.get('cod_estatus','') == '5008':
            #     #break
            # _logger.info(str(result))
            paquete.archivo = result.get('paquete_b64')
            _logger.info('Descargar paquetes, paquete.archivo: ---------------> %s' % result.get('paquete_b64'))
        _logger.info('Descargar paquetes, self: ---------------> %s' % self)
        if self.paquetes:
            self.get_xml()
        # self.descomprimir_paquete()
        # self.extraer_info()
        # self.estatus = 'finalizado'

    def descargar(self):
        self.autenticar()
        self.descargar_paquetes()
        
    def get_xml(self):
        self.descomprimir_paquete()
        self.extraer_info()
        self.estatus = 'finalizado'

    def descomprimir_paquete(self):
        self.cfdis.unlink()
        for paquete in self.paquetes:
            archivo = base64.b64decode(paquete.archivo)
            _logger.info('Descomprimir paquete, archivo: ---------------> %s' % (archivo))
            zipdata = BytesIO()
            _logger.info('Descomprimir paquete, zipdata: ---------------> %s' % (zipdata))
            zipdata.write(archivo)
            myzipfile = zipfile.ZipFile(zipdata)        
            for item in myzipfile.filelist:
                with myzipfile.open(item.filename) as myfile:
                    self.env['xmlsat.cfdi'].create({
                        'solicitud': self.id,
                        'archivo': base64.b64encode(myfile.read()),
                        'filename': 'facturas.zip'
                    })

    def extraer_info(self):
        self.cfdis.extraer_info()

class XmlSatPaquete(models.Model):
    _name = 'xmlsat.paquete'
    _description = 'Paquete'
    id_paquete = fields.Char('Id paquete')
    solicitud = fields.Many2one('xmlsat.solicitud', 'Solicitud', ondelete="cascade")
    archivo = fields.Binary("Archivo comprimido")

class XmlSatCFDI(models.Model):
    _name = 'xmlsat.cfdi'
    _description = 'CFDI'
    _order = 'fecha desc'
    _rec_name = 'uuid'


    solicitud = fields.Many2one('xmlsat.solicitud', 'Solicitud')
    archivo = fields.Binary("Archivo")
    filename = fields.Char("Nombre del archivo")

    version = fields.Char("Versión")
    folio = fields.Char("Folio")
    fecha = fields.Date("Fecha")
    sello = fields.Char("Sello")
    forma_pago = fields.Char("Forma Pago")
    no_certificado = fields.Char("Número Certificado")
    certificado = fields.Char("Certificado")
    sub_total = fields.Float("Subtotal")
    moneda = fields.Char("Moneda")
    total = fields.Float("Total")
    tipo_de_comprobante = fields.Char("Tipo de Comprobante")
    metodo_pago = fields.Char("Método de Pago")
    lugar_expedicion = fields.Char("Lugar de expedición")

    emisor = fields.Many2one('res.partner', 'Emisor')
    emisor_rfc = fields.Char("Emisor RFC")
    emisor_nombre = fields.Char("Emisor Nombre")
    emisor_regimen_fiscal = fields.Char("Emisor Regimen fiscal")

    receptor = fields.Many2one('res.company', 'Receptor')
    receptor_rfc = fields.Char("Receptor RFC")
    receptor_nombre = fields.Char("Receptor Nombre")
    receptor_uso_CFDI = fields.Char("Receptor UsoCFDI")

    total_impuestos_trasladados = fields.Char("Total Impuestos Trasladados")
    
    conceptos = fields.One2many('xmlsat.concepto', 'cfdi', 'Conceptos')

    version = fields.Char("Versión")
    uuid = fields.Char("UUID")
    fecha_timbrado = fields.Date('Fecha timbrado')
    sello_cfd = fields.Char("Sello CFD")
    no_certificado_sat = fields.Char("Número certificado SAT")
    sello_sat = fields.Char("Sello SAT")
    rfc_prov_certif = fields.Char("RfcProvCertif")

    exportada = fields.Boolean('Exportada')
    descartado = fields.Boolean('Descartado')
    estatus = fields.Selection([('nueva','Nueva'),('completa','Completa'),('exportada','Exportada'),('descartada','Descartada')], store=True, compute="get_estatus", string='Estatus')

    def get_estatus(self):
        for item in self:
            if item.exportada:
                item.estatus = 'exportada'
            if item.descartado:
                item.estatus = 'descartada'
            else:
                completa = True
                for concepto in item.conceptos:
                    if not concepto.producto:
                        completa = False
                if not item.emisor:
                    completa = False
                if not item.receptor:
                    completa = False
                if completa:
                    item.estatus = 'completa'
                else:
                    item.estatus = 'nueva'

    def descartar(self):
        for item in self:
            item.write({'descartado':True})

    def procesar(self):
        for item in self:
            account_move_dict = { 
                'ref': item.uuid,
                'invoice_date': item.fecha,
                'date': item.fecha,
                'type': 'in_invoice',
                'partner_id': item.emisor.id,
                # 'commercial_partner_id':item.emisor.id,
                'company_id': item.receptor.id,
                'invoice_line_ids': [], 
            }
            last_account_move = self.env['account.move'].search([('partner_id', '=', item.emisor.id), ('type','=','in_invoice')], order='date desc', limit=1)
            if last_account_move:
                account_move_dict['invoice_payment_term_id'] = last_account_move.invoice_payment_term_id.id


            for concepto in item.conceptos:
                account_move_dict['invoice_line_ids'].append(
                      (0, 0, {
                    'product_id': concepto.producto.id,
                    'quantity': concepto.cantidad,
                    'price_unit': concepto.valor_unitario,
                    'credit': concepto.importe,
                })
                )
            account_move = self.env['account.move'].create(account_move_dict)
            account_move.partner_id = item.emisor.id,
            item.exportada = True
            context = dict(self.env.context)
            context['form_view_initial_mode'] = 'edit'
            return {
            'name': 'Factura CFDI',
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'views': [[False, 'form']],
            'res_id': account_move.id,
            'context': context,
        }

    def extraer_info(self):
        emisor = False #
        uri = '{http://www.sat.gob.mx/cfd/3}'
        tfd = '{http://www.sat.gob.mx/TimbreFiscalDigital}'
        for item in self:
            try:
                decoded_xml = base64.b64decode(item.archivo)
                string_xml = decoded_xml.decode('utf-8')
                tree = ET.fromstring(string_xml)

                item.version = tree.get('Version')
                item.folio = tree.get('Folio')
                item.fecha = tree.get('Fecha')
                item.sello = tree.get('Sello')
                item.forma_pago = tree.get('FormaPago')
                item.no_certificado = tree.get('NoCertificado')
                item.certificado = tree.get('Certificado')
                item.sub_total = tree.get('SubTotal')
                item.moneda = tree.get('Moneda')
                item.total = tree.get('Total')
                item.tipo_de_comprobante = tree.get('TipoDeComprobante')
                item.metodo_pago = tree.get('MetodoPago')
                item.lugar_expedicion = tree.get('LugarExpedicion')

                emisor = tree.find(uri + 'Emisor')
                if emisor is None: #
                    uri = '{http://www.sat.gob.mx/cfd/4}' #
                    emisor = tree.find(uri + 'Emisor') #

                if emisor is not None:
                    partner = self.env['res.partner'].search([('vat','=',emisor.get('Rfc',''))], limit=1)
                    if partner:
                        item.emisor = partner
                    item.emisor_rfc = emisor.get('Rfc')
                    item.emisor_nombre = emisor.get('Nombre')
                    item.emisor_regimen_fiscal = emisor.get('RegimenFiscal')

                receptor = tree.find(uri + 'Receptor')
                if receptor is not None:
                    partner = self.env['res.company'].search(['|',('vat','=',receptor.get('Rfc','')), ('rfc','=',receptor.get('Rfc',''))], limit=1)
                    if partner:
                        item.receptor = partner
                    item.receptor_rfc = receptor.get('Rfc')
                    item.receptor_nombre = receptor.get('Nombre')
                    item.receptor_uso_CFDI = receptor.get('UsoCFDI')
                
                impuestos = tree.find(uri + 'Impuestos')
                if impuestos is not None:
                    item.total_impuestos_trasladados = impuestos.get('TotalImpuestosTrasladados')

                timbre = tree.find(uri + 'Complemento/' + tfd + 'TimbreFiscalDigital')
                if timbre.get('UUID'): #
                    cfdi = self.env['xmlsat.cfdi'].search([('uuid', '=', timbre.get('UUID'))], limit=1) #
                    if cfdi: #
                        item.descartado = True #
                        item.estatus = 'descartada' #
                    else: #
                        # if timbre is not None:
                        item.version = timbre.get('Version')
                        item.uuid = timbre.get('UUID')
                        item.fecha_timbrado = timbre.get('FechaTimbrado')
                        item.sello_cfd = timbre.get('SelloCFD')
                        item.no_certificado_sat = timbre.get('NoCertificadoSAT')
                        item.sello_sat = timbre.get('SelloSAT')
                        item.rfc_prov_certif = timbre.get('RfcProvCertif')

                conceptos = tree.findall(uri + 'Conceptos/' + uri + 'Concepto')
                if conceptos:
                    item.conceptos.unlink()
                    for concepto in conceptos:
                        self.env['xmlsat.concepto'].create({
                            'cfdi': item.id,
                            'clave_unidad': concepto.get('ClaveUnidad'),
                            'clave_prod_serv': concepto.get('ClaveProdServ'),
                            'no_identificacion': concepto.get('NoIdentificacion'),
                            'cantidad': concepto.get('Cantidad'),
                            'unidad': concepto.get('Unidad'),
                            'descripcion': concepto.get('Descripcion'),
                            'valor_unitario': concepto.get('ValorUnitario'),
                            'importe': concepto.get('Importe'),
                        })
                
            except:
                _logger.info('Error en extraer_info CFDI')

class XmlSatConcepto(models.Model):
    _name = 'xmlsat.concepto'
    _description = 'Concepto'

    cfdi = fields.Many2one('xmlsat.cfdi', 'CFDI', ondelete="cascade")
    producto = fields.Many2one('product.product', 'Producto')
    clave_unidad = fields.Char("Clave unidad")
    clave_prod_serv = fields.Char("Clave producto servicio")
    no_identificacion = fields.Char("Número identificación")
    cantidad = fields.Float("Cantidad")
    unidad = fields.Char("Unidad")
    descripcion = fields.Char("Descripción")
    valor_unitario = fields.Float("Valor unitario")
    importe = fields.Float("Importe")

    emisor_rfc = fields.Char("Emisor RFC", related="cfdi.emisor_rfc")
    fecha = fields.Date('Fecha timbrado', related="cfdi.fecha")

    @api.model
    def create(self, values):
        concepto = super(XmlSatConcepto, self).create(values)
        if not concepto.producto:
            concepto_similar = self.env['xmlsat.concepto'].search([('clave_prod_serv','=',concepto.clave_prod_serv),
                                                            ('emisor_rfc', '=', concepto.emisor_rfc),
                                                            ('producto', '!=', False),
                                                            ], order='fecha desc', limit=1)
            if concepto_similar:
                concepto.producto = concepto_similar.producto.id
        return concepto

class ExtCompanySAT(models.Model):
    _inherit = 'res.company'
    _name = 'res.company'

    rfc = fields.Char("RFC")
    fiel_key = fields.Binary(string="Subir FIEL .key")
    fiel_key_filename = fields.Char(string="key filename")
    fiel_cer = fields.Binary(string="Subir FIEL .cer")
    fiel_cer_filename = fields.Char(string="cer filename")
    fiel_password = fields.Char('Contraseña')

