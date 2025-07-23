# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools, _
import base64
from lxml import etree
import requests
from lxml.objectify import fromstring
import io
import logging
from zipfile import ZipFile
from collections import defaultdict
from odoo.exceptions import AccessError

import logging
_logger = logging.getLogger(__name__)

from .special_dict import CaselessDictionary

class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    serie = fields.Char("Serie")
    regimen_emisor = fields.Char("Regimen emisor")
    rfc_emisor = fields.Char("RFC emisor")
    razon_emisor = fields.Char("Razon emisor")
    rfc_receptor = fields.Char("RFC receptor")
    razon_receptor = fields.Char("Razon receptor")
    concepto_text = fields.Char("Conceptos")

    cfdi_iva_cero_t = fields.Float("IVA 0% tras")
    cfdi_iva_16_t = fields.Float("IVA 16% tras")
    cfdi_iva_exe_t = fields.Float("IVA Exento tras")
    cfdi_ieps_t_8 = fields.Float("IEPS tras")
    cfdi_local_t = fields.Float("Imp Local tras")
    cfdi_local_r = fields.Float("Imp Local ret")

    @api.model
    def update_extra_info_xml(self):
        for attach in self:
            wrongfiles = {}
            attachments = {}
            attachment_uuids = {}
            attach_obj = self.env['ir.attachment']
            invoice_obj = self.env['account.move']
            payment_obj = self.env['account.payment']
            company = self.env.company
            company_vat = attach.company_id.vat
            company_id = attach.company_id.id
            NSMAP = {
                     'xsi':'http://www.w3.org/2001/XMLSchema-instance',
                     'cfdi':'http://www.sat.gob.mx/cfd/3', 
                     'tfd': 'http://www.sat.gob.mx/TimbreFiscalDigital',
                     'pago10': 'http://www.sat.gob.mx/Pagos',
                     'implocal': 'http://www.sat.gob.mx/implocal',
                     }
            try:
                xml_str = base64.b64decode(attach.datas)
                # Fix the CFDIs emitted by the SAT
                xml_str = xml_str.replace(b'xmlns:schemaLocation', b'xsi:schemaLocation')
                xml = fromstring(xml_str)
                tree = etree.fromstring(xml_str)
            except Exception as e:
                _logger.error('error : ' + str(e))

            xml_tfd = self.l10n_mx_edi_get_tfd_etree(xml)

            xml_uuid = False if xml_tfd is None else xml_tfd.get('UUID', '')

            if not xml_uuid:
                msg = {'signed': True, 'xml64': True}
                wrongfiles.update({key: msg})
                continue
            else:
                xml_uuid = xml_uuid.upper()

            cfdi_type = xml.get('TipoDeComprobante', 'I')
            receptor = xml.Receptor.attrib or {}
            receptor_rfc = receptor.get('Rfc','')
            if receptor_rfc == company_vat:
                    cfdi_type = 'S'+cfdi_type

            razon_receptor = receptor.get('Nombre','')
            emisor = xml.Emisor.attrib or {}
            rfc_emisor = emisor.get('Rfc','')
            regimen_emisor = emisor.get('RegimenFiscal','')
            razon_emisor = emisor.get('Nombre','')

            try:
                ns = tree.nsmap
                ns.update({'re': 'http://exslt.org/regular-expressions'})
            except Exception:
                ns = {'re': 'http://exslt.org/regular-expressions'}

            cfdi_version = tree.get("Version",'4.0')
            if cfdi_version=='4.0':
                NSMAP.update({'cfdi':'http://www.sat.gob.mx/cfd/4', 'pago20': 'http://www.sat.gob.mx/Pagos20',})
            else:
                NSMAP.update({'cfdi':'http://www.sat.gob.mx/cfd/3', 'pago10': 'http://www.sat.gob.mx/Pagos',})

            if cfdi_type in ['I','E','P','N','T']:
                element_tag = 'Receptor'
            else:
                element_tag = 'Emisor'
            try:
                elements = tree.xpath("//*[re:test(local-name(), '%s','i')]"%(element_tag), namespaces=ns)
            except Exception:
                elements = None

            client_rfc, client_name = '', ''
            if elements:
                attrib_dict = CaselessDictionary(dict(elements[0].attrib))
                client_rfc = attrib_dict.get('rfc') 
                client_name = attrib_dict.get('nombre')

            monto_total = 0
            cfdi_iva = cfdi_isr = cfdi_ieps = cfdi_iva_ret = cfdi_isr_ret = cfdi_ieps_ret = 0
            cfdi_iva_cero_t = cfdi_iva_16_t = cfdi_iva_exe_t = cfdi_ieps_t_8 = cfdi_local_t = cfdi_local_r = 0
            if cfdi_type=='P' or cfdi_type=='SP':
                Complemento = tree.findall('cfdi:Complemento', NSMAP)
                for complementos in Complemento:
                       methodo_pago = None
                       if cfdi_version == '4.0':
                          pagos = complementos.find('pago20:Pagos', NSMAP)
                          pago = pagos.find('pago20:Totales', NSMAP)
                          monto_total = pago.attrib['MontoTotalPagos']
                          forma = pagos.find('pago20:Pago', NSMAP)
                          forma_pago = forma.attrib['FormaDePagoP']
                       else:
                          pagos = complementos.find('pago10:Pagos', NSMAP)
                          try:
                             pago = pagos.find('pago10:Pago',NSMAP)
                             monto_total = pago.attrib['Monto']
                             forma_pago = pago.attrib['FormaDePagoP']
                          except Exception as e:
                             for payment in pagos.find('pago10:Pago',NSMAP):
                                monto_total += float(payment.attrib['Monto'])
                                forma_pago = pago.attrib['FormaDePagoP']
                       if pagos is not None:
                           break
            else:
                monto_total = tree.get('Total', tree.get('total'))
                forma_pago = tree.get("FormaPago", '')
                methodo_pago = tree.get("MetodoPago", '')

                todos_impuestos = tree.find('cfdi:Impuestos', NSMAP)
                if todos_impuestos is not None:
                   traslados = todos_impuestos.find('cfdi:Traslados', NSMAP)
                   retenciones = todos_impuestos.find('cfdi:Retenciones', NSMAP)
                   if traslados is not None:
                      for traslado in traslados:
                          if traslado.attrib['Impuesto'] == '002' and traslado.attrib['TipoFactor'] != "Exento":
                             cfdi_iva += float(traslado.attrib['Importe'])
                             if traslado.attrib['TasaOCuota'] == "0.160000":
                                cfdi_iva_16_t += float(traslado.attrib['Importe'])
                             if traslado.attrib['TasaOCuota'] == "0.000000":
                                cfdi_iva_cero_t += float(traslado.attrib['Base'])

                          if traslado.attrib['Impuesto'] == '001':
                             cfdi_isr += float(traslado.attrib['Importe'])
                          if traslado.attrib['Impuesto'] == '003':
                             cfdi_ieps += float(traslado.attrib['Importe'])
                             if traslado.attrib['TasaOCuota'] == "0.080000":
                                cfdi_ieps_t_8 += float(traslado.attrib['Importe'])

                          if traslado.attrib['Impuesto'] == '002' and traslado.attrib['TipoFactor'] == "Exento":
                             cfdi_iva_exe_t += float(traslado.attrib['Base'])

                   if retenciones is not None:
                      for retencion in retenciones:
                          if retencion.attrib['Impuesto'] == '002':
                             cfdi_iva_ret += float(retencion.attrib['Importe'])
                          if retencion.attrib['Impuesto'] == '001':
                             cfdi_isr_ret += float(retencion.attrib['Importe'])
                          if retencion.attrib['Impuesto'] == '003':
                             cfdi_ieps_ret += float(retencion.attrib['Importe'])

            concepto_text = None
            if cfdi_type in ['I','E']:
               conceptos = tree.find('cfdi:Conceptos', NSMAP)
               for concepto in conceptos:
                  if concepto_text:
                     concepto_text += ' | ' + concepto.get('Descripcion', '')
                  else:
                     concepto_text = concepto.get('Descripcion', '')

            serie = xml.get("Serie", '') 

            receptor = tree.find('cfdi:Receptor', NSMAP)
            uso_cfdi = receptor.attrib['UsoCFDI']

            cfdi_condicion_pago = xml.get('CondicionesDePago', '')
            cfdi_subtotal = xml.get('SubTotal', '')
            cfdi_descuento = xml.get('Descuento', '')

            nodo_relacionado = tree.find('cfdi:CfdiRelacionados', NSMAP)
            if nodo_relacionado:
                    tipo_relacion = nodo_relacionado.attrib['TipoRelacion']
            else:
                    tipo_relacion = ''


            complemento = tree.find('cfdi:Complemento', NSMAP)
            local_taxes = complemento.find('implocal:ImpuestosLocales', NSMAP)
            if local_taxes is not None:
                cfdi_local_t = local_taxes.get('TotaldeTraslados', '')
                cfdi_local_r = local_taxes.get('TotaldeRetenciones', '')

            vals = {
                    'methodo_pago' : methodo_pago,
                    'forma_pago' : forma_pago,
                    'uso_cfdi' : uso_cfdi,
                    'tipo_relacion' : tipo_relacion,
                    'cfdi_condicion_pago' : cfdi_condicion_pago,
                    'cfdi_subtotal' : cfdi_subtotal,
                    'cfdi_descuento' : cfdi_descuento,

                    'cfdi_iva' : cfdi_iva,
                    'cfdi_isr' : cfdi_isr,
                    'cfdi_ieps' : cfdi_ieps,
                    'cfdi_iva_ret' : cfdi_iva_ret,
                    'cfdi_isr_ret' : cfdi_isr_ret, 
                    'cfdi_ieps_ret' : cfdi_ieps_ret,

                    'serie' : serie,
                    'rfc_emisor' : rfc_emisor,
                    'regimen_emisor' : regimen_emisor,
                    'razon_emisor' : razon_emisor,
                    'rfc_receptor' : receptor_rfc,
                    'razon_receptor' : razon_receptor,
                    'concepto_text' : concepto_text,
                    'cfdi_iva_cero_t' : cfdi_iva_cero_t,
                    'cfdi_iva_16_t' : cfdi_iva_16_t,
                    'cfdi_iva_exe_t' : cfdi_iva_exe_t,
                    'cfdi_ieps_t_8' : cfdi_ieps_t_8,
                    'cfdi_local_t' : cfdi_local_t,
                    'cfdi_local_r' : cfdi_local_r,
            }
            attach.update(vals)
