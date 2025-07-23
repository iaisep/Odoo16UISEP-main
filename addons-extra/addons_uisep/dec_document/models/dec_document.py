import base64
import logging
from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_round
from lxml import etree 

_logger = logging.getLogger(__name__)


class OpCourse(models.Model):
    _inherit = 'op.course'

    id_carrera = fields.Char(string='Id de Carrera')
    calificacion_minima = fields.Integer(string="Calificación Mínima", default=5)
    calificacion_maxima = fields.Integer(string="Calificación Máxima", default=10)
    calificacion_minima_aprobatoria = fields.Integer(string="Calificación Mínima Aprobatoria", default=8)

class DecAsignatura(models.Model):
    _name = 'dec.asignatura'
    _description = 'Asignatura'

    dec_id = fields.Many2one('dec.document', string='Documento DEC')
    clave_asignatura = fields.Char(string='Clave', required=True)
    calificacion = fields.Float(string='Calificación', required=True)
    creditos = fields.Integer(string='Créditos', required=True)
    ciclo = fields.Char(string="Ciclo")
    id_tipo_asignatura = fields.Char(string="Id Tipo Asignatura", default="263")
    id_observaciones = fields.Char(string="Id Observaciones", default="100")


class DecDocument(models.Model):
    _name = 'dec.document'
    _description = 'Documento Electrónico de Certificación (DEC)'
    _rec_name='folio_control'
    
    id_campus = fields.Char(string='ID Campus', required=True, default="250218", readonly=True)
    ides_ipes = fields.Char(string='ID IPES', required=True, default="21098", readonly=True)
    fecha_emision = fields.Datetime(string='Fecha de Emisión', default=fields.Datetime.now, required=True)
    id_cargo = fields.Char(string="Id Cargo", default="1", readonly=True)
    responsable_id = fields.Many2one('res.partner', string='Responsable', required=True)
    resp_curp = fields.Char(string='Curp Responsable', required=True, compute="_compute_resp")
    resp_name = fields.Char(string='Nombre del Responsable', required=True, compute="_compute_resp")
    resp_primer_apellido = fields.Char(string="Primer Apellido Resp", compute="_compute_resp")
    resp_segundo_apellido = fields.Char(string="Segundo Apellido Resp", compute="_compute_resp")
    rvoe = fields.Char(string='RVOE', required=True)
    fecha_rvoe = fields.Datetime(string='Fecha Rvoe', default=fields.Datetime.now, required=True)
    curp_alumno = fields.Char(string='CURP', size=18, required=True)
    alumno_nombre = fields.Char(string='Nombre del Alumno', required=True)
    primer_apellido = fields.Char(string="Primer Apellido")
    segundo_apellido = fields.Char(string="Segundo Apellido")
    programa_estudio = fields.Char(string='Programa de Estudio', required=True)
    asignaturas_line = fields.One2many('dec.asignatura', 'dec_id', string='Asignaturas')
    sello_dreoe = fields.Text(string='Sello DREOE')
    sello_sepipes = fields.Text(string='Sello SEPIPES')
    xml_file = fields.Binary(string='XML Generado', attachment=True)
    xml_filename = fields.Char(string='Nombre del Archivo XML')
    estado = fields.Selection([('borrador', 'Borrador'), ('sellado', 'Sellado')], string='Estado', default='borrador')
    timestamp = fields.Text(string='Timestamp')
    state_id = fields.Many2one('res.country.state', string="Entidad Federativa / Lugar Exp", default= lambda s: s.env['res.country.state'].search([('code','=','25'),('country_id.l10n_mx_edi_code','=','MEX')], limit=1).id )
    programa_estudio_tipo = fields.Char(string="Tipo de Periodo")
    clave_plan = fields.Char(string="Clave Plan")
    nivel_estudios = fields.Char(string="Nivel de Estudios")
    calificacion_minima = fields.Integer(string="Calificación Mínima", default=5)
    calificacion_maxima = fields.Integer(string="Calificación Máxima", default=10)
    calificacion_minima_aprobatoria = fields.Integer(string="Calificación Mínima Aprobatoria", default=8)
    numero_control = fields.Char(string="Numero de Control")
    id_genero = fields.Selection(selection=[('251','Masculino'),('250','Femenino')],string="Id Genero", default="250")
    fecha_nacimiento = fields.Datetime(string="Fecha de Nacimiento")
    id_tipo_certificacion = fields.Selection(selection=[('80','Parcial'),('79','Total')], string="Id Tipo Certificacion", default='79')
    fecha_expedicion = fields.Datetime(string="Fecha de Expedicion", default=fields.Datetime.now, required=True)
    total = fields.Integer(string="Total",required=True)
    asignadas = fields.Integer(string="Asignadas", compute="_compute_totals")
    promedio = fields.Float(string="Promedio", compute ="_compute_totals")
    total_creditos = fields.Integer(string="Total Creditos", required=True)
    creditos_obtenidos = fields.Integer(string="Creditos Obtenidos", compute="_compute_totals")
    numero_ciclos = fields.Integer(string="Numero Ciclos")
    tipo_certificado = fields.Char(string="Tipo Certificado", default="5")
    folio_control = fields.Char(string="Folio Control", readonly=True, default=lambda self: self.env['ir.sequence'].next_by_code('dec.document.sequence'))
    

    def _compute_totals(self):
        for dec in self:
            dec.asignadas = len(dec.asignaturas_line.ids)
            dec.promedio = float_round(sum([a.calificacion for a in dec.asignaturas_line])/dec.asignadas, 2)
            dec.creditos_obtenidos = sum([a.creditos for a in dec.asignaturas_line])
             

    def _compute_resp(self):
        for dec in self:
            dec.resp_name = dec.responsable_id and dec.responsable_id.name.split()[0] or ''
            dec.resp_primer_apellido = dec.responsable_id and len(dec.responsable_id.name.split()) >1 and dec.responsable_id.name.split()[1] or ''
            dec.resp_segundo_apellido = dec.responsable_id and len(dec.responsable_id.name.split()) >2 and dec.responsable_id.name.split()[2] or ''
            dec.resp_curp = dec.responsable_id and dec.responsable_id.l10n_mx_edi_curp or ''


    def unlink(self):
        for record in self:
            if record.xml_file or record.estado == 'sellado':
                raise ValidationError(_('No se puede eliminar el registro con archivo xml'))
        return super(DecDocument, self).unlink()

    def _generate_cadena_original(self):
        """Genera cadena original según especificación SEP 3.0 sección 6.5"""
        elements = []

        company_id = self.env.company
        certificates = company_id.op_sign_certificate_ids.filtered(lambda c: c.dec_certificate)
        certificate_id = certificates._get_valid_certificate()
         
        # 1. Version
        elements.append("3.0")

        # 2. Datos institucionales (IPES)
        elements.append(self.ides_ipes or '')  # ID IPES
        elements.append(self.env.company.name or '')  # Nombre Institución
        elements.append(self.env.company.street or '')  # Domicilio
        elements.append(self.state_id.code or '')  # Entidad Federativa

        # 3. Datos del responsable (RESPONSABLE)
        elements.append(self.resp_name or '')  # Nombre del Responsable
        elements.append(certificate_id.serial_number or '')  # Número de Certificado digital del Responsable
        elements.append(self.fecha_emision.strftime("%Y-%m-%dT%H:%M:%S") or '')  # Fecha de Emisión (YYYY-MM-DDTHH:MM:SS)

        # 4. Datos del RVOE (RVOE)
        elements.append(self.rvoe or '')  # Clave del RVOE
        elements.append(self.fecha_rvoe.strftime("%Y-%m-%dT%H:%M:%S") or '')  # Fecha de Otorgamiento (YYYY-MM-DDTHH:MM:SS)

        # 5. Datos de la Carrera (CARRERA)
        elements.append(self.programa_estudio or '') # Nombre de la Carrera
        elements.append(self.programa_estudio_tipo or '') # Tipo de Periodo
        elements.append(self.clave_plan or '')  # Clave de Plan
        elements.append(self.nivel_estudios or '') # Nivel de estudios

        # 6. Calificaciones
        elements.append(str(self.calificacion_minima) or '')  # Calificación mínima
        elements.append(str(self.calificacion_maxima) or '')  # Calificación máxima
        elements.append(str(self.calificacion_minima_aprobatoria) or '') # Calificación mínima aprobatoria

        # 7. Datos del Alumno (ALUMNO)
        elements.append(self.curp_alumno or '')  # CURP del Alumno
        elements.append(self.alumno_nombre or '')  # Nombre del Alumno
        elements.append(self.primer_apellido or '')  # Primer Apellido
        elements.append(self.segundo_apellido or '')  # Segundo Apellido
        elements.append(self.id_genero or '')  # Id Genero
        elements.append(self.fecha_nacimiento.strftime("%Y-%m-%dT%H:%M:%S") or '')  # Fecha de nacimiento (YYYY-MM-DDTHH:MM:SS)

        # 8. Tipo Certificacion
        elements.append(self.id_tipo_certificacion or '')  # id Tipo Certificación

        # 9. Expedicion
        elements.append(self.fecha_expedicion.strftime("%Y-%m-%dT%H:%M:%S") or '') # Fecha Expedición

        #10 Lugar Expedicion
        elements.append(self.state_id.code or '') #id Lugar Expedicion

        #11 Totales
        elements.append(str(self.total) or '')
        elements.append(str(self.asignadas) or '')
        elements.append(str(self.promedio) or '')
        elements.append(str(self.total_creditos) or '')
        elements.append(str(self.creditos_obtenidos) or '')
        elements.append(str(self.numero_ciclos) or '')

        # 12. Datos de las Asignaturas (ASIGNATURAS)
        asignaturas_data = []
        for asignatura in self.asignaturas_line:
            asignaturas_data.append(str(asignatura.clave_asignatura) or '') # id Asignatura
            asignaturas_data.append(str(asignatura.ciclo) or '') # Ciclo
            asignaturas_data.append(str(asignatura.calificacion) or '')  # Calificación
            asignaturas_data.append(str(asignatura.id_tipo_asignatura) or '')  # Id Tipo Asignatura
            asignaturas_data.append(str(asignatura.creditos) or '')  # Creditos

        elements.append("|".join(asignaturas_data))


        # Validation of required fields (sección 6.3) - Keep validation
        required_fields = {
            'ID IPES': self.ides_ipes,
            'Certificado responsable': certificate_id.serial_number,
            'CURP alumno': self.curp_alumno,
            'RVOE': self.rvoe
        }

        missing = [k for k, v in required_fields.items() if not v]
        if missing:
            raise UserError(_("Campos requeridos faltantes: %s") % ", ".join(missing))

        return "||" + "|".join(elements) + "||"

    def _sign_xml(self):
        """Signs the XML with the certificate and private key."""
        self.ensure_one()
        cadena = self._generate_cadena_original()
       
        # Retrieve certificate and key paths from system parameters
        try:
            company_id = self.env.company
            certificates = company_id.op_sign_certificate_ids.filtered(lambda c: c.dec_certificate)
            certificate_id = certificates._get_valid_certificate()
            sello = certificate_id._get_encrypted_cadena(cadena)
            self.sello_dreoe = sello # Save the seal as base64

        except Exception as e:
            _logger.error("Error signing the XML: %s", str(e))
            raise UserError(_("Error signing the XML: %s") % str(e))
        values={
            'certificate_number': certificate_id.serial_number,
            'certificate_key': certificate_id.sudo()._get_data()[0].decode('utf-8'),
            }
        self.generate_xml(values)  # Generate the XML after signing
        self.estado = 'sellado'

    def generate_xml(self, values={}):
        """Generates the XML from the QWeb template."""
        self.ensure_one()
        values.update({'doc': self})
        xml_content = self.env['ir.qweb']._render('dec_document.dec_document_xml', values)
        xml_pretty = etree.tostring(etree.fromstring(xml_content), pretty_print=True, encoding='UTF-8', xml_declaration=True).decode()

        # Validate against XSD
        try:
            self.validate_xml(xml_pretty)  # Validate before saving
        except Exception as e:
            raise UserError(_("Error al validar el XML: %s") % str(e))

        # Save the XML content in a binary field
        filename = f"{self.curp_alumno}_{self.rvoe}.xml"  # Filename format
        self.xml_file = base64.b64encode(xml_pretty.encode('utf-8'))
        self.xml_filename = filename  # Store the filename

        return xml_content  # Return the content if necessary

    def action_bulk_sign(self):
        """Signs multiple documents."""
        for record in self:
            if record.estado == 'borrador':
                record._sign_xml()

    def action_sign(self):
        """Signs the current document."""
        self.ensure_one()
        self._sign_xml()


    def action_download_xml(self):
        self.ensure_one()
        if not self.xml_file:
            return False
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/?model={self._name}&id={str(self.id)}&field=xml_file&download=true&filename={self.xml_filename}',
            'target': 'self',
        }        

    def validate_xml(self, xml_string):
        """Validates the XML against the XSD schema."""
        with tools.file_open('dec_document/data/xsd/certificado.xsd', 'rb') as xsd:
            tools.xml_utils._check_with_xsd(xml_string.encode('UTF-8'), xsd)


