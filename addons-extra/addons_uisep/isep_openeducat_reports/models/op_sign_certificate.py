# -*- coding: utf-8 -*-
import zlib
import json
import hashlib
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import utils
from cryptography.hazmat.backends import default_backend
import base64
import logging
import ssl
import subprocess
import tempfile
from datetime import datetime

_logger = logging.getLogger(__name__)

try:
    from OpenSSL import crypto
except ImportError:
    _logger.warning('OpenSSL library not found. If you plan to use l10n_mx_edi, please install the library from https://pypi.python.org/pypi/pyOpenSSL')

from pytz import timezone

from odoo import _, api, fields, models, tools
from odoo.exceptions import ValidationError, UserError
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT


KEY_TO_PEM_CMD = 'openssl pkcs8 -in %s -inform der -outform pem -out %s -passin file:%s'


def convert_key_cer_to_pem(key, password):
    # TODO compute it from a python way
    with tempfile.NamedTemporaryFile('wb', suffix='.key', prefix='edi.mx.tmp.') as key_file, \
            tempfile.NamedTemporaryFile('wb', suffix='.txt', prefix='edi.mx.tmp.') as pwd_file, \
            tempfile.NamedTemporaryFile('rb', suffix='.key', prefix='edi.mx.tmp.') as keypem_file:
        key_file.write(key)
        key_file.flush()
        pwd_file.write(password)
        pwd_file.flush()
        subprocess.call((KEY_TO_PEM_CMD % (key_file.name, keypem_file.name, pwd_file.name)).split())
        key_pem = keypem_file.read()
    return key_pem


def str_to_datetime(dt_str, tz=timezone('America/Mexico_City')):
    return tz.localize(fields.Datetime.from_string(dt_str))


class Certificate(models.Model):
    _name = 'op.sign_certificate'
    _description = 'Certificate for Student Certificates'
    _order = "date_start desc, id desc"

    content = fields.Binary(
        string='Certificate',
        help='Certificate in der format',
        required=True,
        attachment=False,)
    key = fields.Binary(
        string='Certificate Key',
        help='Certificate Key in der format',
        required=True,
        attachment=False,)
    password = fields.Char(
        string='Certificate Password',
        help='Password for the Certificate Key',
        required=True,)
    serial_number = fields.Char(
        string='Serial number',
        help='The serial number to add to electronic documents',
        readonly=True,
        index=True)
    date_start = fields.Datetime(
        string='Available date',
        help='The date on which the certificate starts to be valid',
        readonly=True)
    date_end = fields.Datetime(
        string='Expiration date',
        help='The date on which the certificate expires',
        readonly=True)

    @tools.ormcache('content')
    def _get_pem_cer(self, content):
        '''Get the current content in PEM format
        '''
        self.ensure_one()
        return ssl.DER_cert_to_PEM_cert(base64.decodebytes(content)).encode('UTF-8')

    @tools.ormcache('key', 'password')
    def _get_pem_key(self, key, password):
        '''Get the current key in PEM format
        '''
        self.ensure_one()
        return convert_key_cer_to_pem(base64.decodebytes(key), password.encode('UTF-8'))

    def _get_data(self):
        '''Return the content (b64 encoded) and the certificate decrypted
        '''
        self.ensure_one()
        cer_pem = self._get_pem_cer(self.content)
        certificate = crypto.load_certificate(crypto.FILETYPE_PEM, cer_pem)
        for to_del in ['\n', ssl.PEM_HEADER, ssl.PEM_FOOTER]:
            cer_pem = cer_pem.replace(to_del.encode('UTF-8'), b'')
        return cer_pem, certificate

    def get_mx_current_datetime(self):
        '''Get the current datetime with the Mexican timezone.
        '''
        return fields.Datetime.context_timestamp(
            self.with_context(tz='America/Mexico_City'), fields.Datetime.now())

    def _get_valid_certificate(self):
        '''Search for a valid certificate that is available and not expired.
        '''
        mexican_dt = self.get_mx_current_datetime()
        for record in self:
            date_start = str_to_datetime(record.date_start)
            date_end = str_to_datetime(record.date_end)
            if date_start <= mexican_dt <= date_end:
                return record
        return None

    def _get_encrypted_cadena(self, cadena):
        '''Encrypt the cadena using the private key.
        '''
        self.ensure_one()
        key_pem = self._get_pem_key(self.key, self.password)
        private_key = crypto.load_privatekey(crypto.FILETYPE_PEM, bytes(key_pem))
        encrypt = 'sha256WithRSAEncryption'
        cadena_crypted = crypto.sign(private_key, bytes(cadena.encode()), encrypt)
        return base64.b64encode(cadena_crypted)

    @api.constrains('content', 'key', 'password')
    def _check_credentials(self):
        '''Check the validity of content/key/password and fill the fields
        with the certificate values.
        '''
        mexican_tz = timezone('America/Mexico_City')
        mexican_dt = self.get_mx_current_datetime()
        date_format = '%Y%m%d%H%M%SZ'
        for record in self:
            # Try to decrypt the certificate
            try:
                certificate = record._get_data()[1]
                before = mexican_tz.localize(
                    datetime.strptime(certificate.get_notBefore().decode("utf-8"), date_format))
                after = mexican_tz.localize(
                    datetime.strptime(certificate.get_notAfter().decode("utf-8"), date_format))
                serial_number = certificate.get_serial_number()
            except UserError as exc_orm:  # ;-)
                raise exc_orm
            except Exception as e:
                raise ValidationError(_('The certificate content is invalid %s.', e))
            # Assign extracted values from the certificate
            record.serial_number = ('%x' % serial_number)[1::2]
            record.date_start = before.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            record.date_end = after.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            if mexican_dt > after:
                raise ValidationError(_('The certificate is expired since %s', record.date_end))
            # Check the pair key/password
            try:
                key_pem = self._get_pem_key(self.key, self.password)
                crypto.load_privatekey(crypto.FILETYPE_PEM, key_pem)
            except Exception:
                raise ValidationError(_('The certificate key and/or password is/are invalid.'))

    @api.ondelete(at_uninstall=True)
    def _unlink_except_attachments(self):
        if self.env['ir.attachment'].sudo().search([
            ('sign_certificate_id', '=', self.id)
        ], limit=1):
            raise UserError(_(
                'You cannot remove a certificate if at least an attachment has been signed. '
                'Expired Certificates will not be used as Odoo uses the latest valid certificate. '
                'To not use it, you can unlink it from the current company certificates.'))

    def stamp_data(self, data, student=False):
        if student:
            company_id = student and student.company_id or False
        else:
            company_id = self.env['res.company'].search([('id','=',self.env.company.id)])
        certificates = company_id.op_sign_certificate_ids
        certificate_id = certificates._get_valid_certificate()
        if not certificate_id:
            return {}
        data_str = json.dumps(data, sort_keys=True)
        compressed_data_str= zlib.compress(data_str.encode('utf-8'))
        data_str_enc = base64.b64encode(compressed_data_str).decode('utf-8')
        cadena_cript = certificate_id._get_encrypted_cadena(data_str)
        compressed_cadena_cript = zlib.compress(cadena_cript)
        cadena_cript_enc = base64.b64encode(compressed_cadena_cript).decode('utf-8')
        return {'stamp': cadena_cript_enc, 'certificate_id': certificate_id.id, 'data_str': data_str_enc}


    def web_verify_certificate(self, data):
        res = {'Resultado de la Validación':'Documento Inválido'}
        data_str_enc = data.get('data_str', False)
        if not data_str_enc:
            return res
        compressed_data_str= base64.b64decode(data_str_enc)
        data_str = zlib.decompress(compressed_data_str).decode('utf-8')
        certificate = data.get('certificate_id', False)
        if not certificate:
            return res
        cadena_enc = data.get('stamp', False)
        if not cadena_enc:
            return res
        compressed_cadena = base64.b64decode(cadena_enc)
        cadena = zlib.decompress(compressed_cadena).decode('utf-8')

        certificate_id = self.env['op.sign_certificate'].browse([int(certificate)])
        if certificate_id and cadena:
            cer_pem =certificate_id._get_pem_cer(certificate_id.content)
            result = self.verify_signature(cer_pem, data_str, cadena)
            if result:
                res = json.loads(data_str)
                  
                res['Resultado de la Validación'] = 'Documento Válido'
        return res

    def verify_signature(self, pem_cert, original_data, signature_base64):
        # Load the certificate from PEM format
        cert = x509.load_pem_x509_certificate(pem_cert)
        
        # Extract the public key from the certificate
        public_key = cert.public_key()
        
        # Decode the Base64-encoded signature
        signature = base64.b64decode(signature_base64)
        
        # Verify the signature
        try:
            public_key.verify(
                signature,
                original_data.encode(),  # The original data, encoded as bytes
                padding.PKCS1v15(),
                hashes.SHA256()  # Hash algorithm used when signing
            )
            return True  # Signature is valid
        except Exception as e:
            return False  # Signature is invalid
    


