# -*- coding: utf-8 -*-
import base64
import logging


from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)

class PracticeRequest(models.Model):
    _name = 'practice.request'
    _description = 'Practice Request'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string="Student Name",
        required=True,
        help="Name of the student submitting the request."
    )
    
    op_student_id = fields.Many2one('op.student', string='Estudiante', related="op_admission_id.student_id" , store=True)
    op_admission_id = fields.Many2one("op.admission", 'Admisión')
    
    email = fields.Char(
        string="Email",
        required=True,
        help="Email address of the student."
    )
    course_id = fields.Many2one(
        'op.student.course',
        string="Course",
        required=True,
        help="The course the student is enrolling in."
    )
    
    user_id = fields.Many2one(
        'res.users',
        string="Usuario Estudiante",
        required=True,
    )
    
    op_student_course_course_id = fields.Many2one(related="course_id.course_id")
    practice_center_type_id = fields.Many2one(
        'practice.center.type',
        string="Practice Type",
        required=True,
        help="The modality the student wants to opt for."
    )
    practice_center_type_id_total_hours = fields.Float(related="practice_center_type_id.total_hours",store=True)

    application_description = fields.Text(
        string="Additional Information",
        help="Any additional information provided by the student."
    )
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('assigned', 'Asignado'),
        ('approved', 'Aprobado'),
        ('rejected', 'Rechazado'),
        ('progress', 'En Proceso'),
        ('end', 'Finalizado'),
    ], string="Estado", default='draft', tracking=True, help="State of the practice request.")

    request_date = fields.Datetime(
        string="Request Date",
        default=fields.Datetime.now,
        help="Date and time the request was submit."
    )
    country_id = fields.Many2one('res.country', string='Country', default=lambda self: self.env.company.country_id)
    state_id = fields.Many2one('res.country.state', string="State", domain="[('country_id', '=?', country_id)]")
    zip_id = fields.Many2one(
        "res.city.zip",
        string="ZIP Location",
        help="Use the city name or the zip code to search the location",
        domain="[('state_id', '=?', state_id)]"
    )

    solicited_practice_center_ids = fields.Many2many(
        'practice.center',
        string="Solicited Practice Center",
        help="The practice center where the student will solicited the practices.",
    )

    practice_center_id = fields.Many2one(
        'practice.center',
        string="Assigned Practice Center",

        help="The practice center where the student will do the practices.",
        domain="[('id','in',solicited_practice_center_ids)]"
    )

    available_practice_centers_ids = fields.Many2many(
        'practice.center',
        string="Available Practice Centers",
        compute="_compute_available_practice_centers",
        help="List of available practice centers based on the selected type and course."
    )
    monday_available_start_time = fields.Float(
        string="Monday Start Time",
        help="Start time available on Monday."
    )
    monday_available_end_time = fields.Float(
        string="Monday End Time",
        help="End time available on Monday."
    )

    tuesday_available_start_time = fields.Float(
        string="Tuesday Start Time",
        help="Start time available on Tuesday."
    )
    tuesday_available_end_time = fields.Float(
        string="Tuesday End Time",
        help="End time available on Tuesday."
    )

    wednesday_available_start_time = fields.Float(
        string="Wednesday Start Time",
        help="Start time available on Wednesday."
    )
    wednesday_available_end_time = fields.Float(
        string="Wednesday End Time",
        help="End time available on Wednesday."
    )

    thursday_available_start_time = fields.Float(
        string="Thursday Start Time",
        help="Start time available on Thursday."
    )
    thursday_available_end_time = fields.Float(
        string="Thursday End Time",
        help="End time available on Thursday."
    )

    friday_available_start_time = fields.Float(
        string="Friday Start Time",
        help="Start time available on Friday."
    )
    friday_available_end_time = fields.Float(
        string="Friday End Time",
        help="End time available on Friday."
    )

    saturday_available_start_time = fields.Float(
        string="Saturday Start Time",
        help="Start time available on Saturday."
    )
    saturday_available_end_time = fields.Float(
        string="Saturday End Time",
        help="End time available on Saturday."
    )

    sunday_available_start_time = fields.Float(
        string="Sunday Start Time",
        help="Start time available on Sunday."
    )
    sunday_available_end_time = fields.Float(
        string="Sunday End Time",
        help="End time available on Sunday."
    )

    start_date = fields.Date(
        string="Start Practice Date",
        default=fields.Datetime.now,
        help="Date and time the Start Practice."
    )
    final_date = fields.Date(
        string="Final Practice Date",
        default=fields.Datetime.now,
        help="Date and time the End Practice."
    )
    total_hours = fields.Float(
        string="Total hours",
        help="Total hours of practices"
    )
    tutor_id = fields.Many2one('res.partner',
                               string="Tutor",
                               domain=[('tutor', '=', True)], )

    sign_request_specific_agrement_id = fields.Integer()
    sign_request_framework_agrement_id = fields.Integer()
    email_send = fields.Selection([
        ('framework_specific', 'Acuerdo de condiciones y Convenio Especifico enviados por correo'),
        ('not_send', 'Convenios no enviados'), ], 'Estado de Convenio', track_visibility='onchange')
    status_sign_specific = fields.Selection([
        ('Signatures Pending', 'Firma en Trámite'),
        ('Fully Signed', 'Totalmente Firmado'),
        ('cancelled', 'Cancelado'), ], 'Estado de firma del convenio específico', track_visibility='onchange',
        compute="_status_sign")
    status_sign_framework = fields.Selection([
        ('Signatures Pending', 'Firma en Trámite'),
        ('Fully Signed', 'Totalmente Firmado'),
        ('cancelled', 'Cancelado'), ], 'Estado de firma del Acuerdo de condiciones', track_visibility='onchange',
        compute="_status_sign")

    request_document_ids = fields.One2many('practice.request.document',
                                           'practice_request_id',
                                           string='Documents')

    attachment_ids = fields.Many2many('ir.attachment', 'practice_request_documents', 'practice_request_id',
                                      'res_id', domain=lambda self: [('res_model', '=', 'practice.request')],
                                      string='Adjuntos',
                                      )
    attachment2_ids = fields.Many2many('ir.attachment', 'practice_request_documents', 'practice_request_id',
                                       'res_id', domain=lambda self: [('res_model', '=', 'practice.request')],
                                       string='Adjuntos',
                                       )

    checklist_ids = fields.One2many(
        'practice.request.checklist',
        'practice_request_id',
        string="Checklist Items",
        help="Checklist items linked to this practice request."
    )

    checklist_completed = fields.Boolean(
        string="Checklist Completed",
        compute="_compute_checklist_completed",
        store=True,
        help="Indicates if all mandatory items in the checklist are marked as done."
    )
    total_available_hours = fields.Float(
        string="Total Available Hours for the week.",
        compute='_compute_total_available_hours',
        store=True,
        help="Total available hours for the week."
    )
    weeks_practices = fields.Float(
        string="Weeks of practices",
        compute='_compute_total_available_hours',
        store=True,
        help="Number of weeks the practice will last."
    )
    compute_final_date = fields.Date(
        string="Posible Final Practice Date",
        help="Date and time the End Practice.",
        compute="_compute_final_date"
    )
    
    attachment_upload_ids = fields.One2many(
        'ir.attachment', 'res_id', string="Archivos Subidos", compute="_compute_attachments"
    )

    @api.depends('email')
    def _compute_attachments(self):
        for record in self:
            if record.email:
                attachments = self.env['ir.attachment'].sudo().search([
                    ('create_uid.partner_id.email', '=', record.email),
                    ('res_id', '=', False),
                    ('res_model', '=', False),
                    ('website_id', '!=', False)
                ])
                record.attachment_upload_ids = attachments
            else:
                record.attachment_upload_ids = False
                

    @api.depends('monday_available_start_time', 'monday_available_end_time',
                 'tuesday_available_start_time', 'tuesday_available_end_time',
                 'wednesday_available_start_time', 'wednesday_available_end_time',
                 'thursday_available_start_time', 'thursday_available_end_time',
                 'friday_available_start_time', 'friday_available_end_time',
                 'saturday_available_start_time', 'saturday_available_end_time'
                 )
    def _compute_total_available_hours(self):
        for record in self:
            """Calculates the total available hours across all days of the week."""
            total_hours = 0

            # Iterate over each day of the week and calculate the difference between end and start times
            for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
                start_time = getattr(record, f"{day}_available_start_time")
                end_time = getattr(record, f"{day}_available_end_time")
                total_hours += end_time - start_time


            record.total_available_hours = total_hours
            record.weeks_practices =False
            if record.total_available_hours>0:
                record.weeks_practices=record.practice_center_type_id_total_hours/record.total_available_hours
            record._compute_final_date()



    @api.depends('start_date', 'weeks_practices')
    def _compute_final_date(self):
        for record in self:
            if record.start_date and record.weeks_practices:
                # Añadir semanas a la fecha de inicio
                record.compute_final_date = record.start_date + relativedelta(weeks=record.weeks_practices)
            else:
                record.compute_final_date =False


    # @api.depends('monday_available_start_time', 'monday_available_end_time', ...)
    # def _compute_total_available_hours(self):
    #     for record in self:
    #         record.total_available_hours = self.total_available_hours(record)

    @api.onchange('status_sign_specific', 'status_sign_framework')
    def _check_status_and_update(self):
        # Verificar si ambos campos están en 'Fully Signed'
        if self.status_sign_specific == 'Fully Signed' and self.status_sign_framework == 'Fully Signed':
            self.state = 'progress'

    @api.model
    def create(self, vals):
        """Envía correo al crear el registro si se requiere."""
        record = super(PracticeRequest, self).create(vals)
        record._send_email_notification()  # Envía correo al crear si es necesario
        record.generate_checklist() 
        return record

    def write(self, vals):
        """Detecta cambios en el estado y envía correo de notificación."""
        for record in self:
            old_state = record.state
            super(PracticeRequest, record).write(vals)

            # Si el estado cambió, enviar notificación
            if 'state' in vals and vals['state'] != old_state:
                record._send_email_notification()
        return True

    def _send_email_notification(self):
        """Envía una notificación por correo al tutor y al estudiante."""
        for record in self:
            # Validar que existan correos para estudiante y tutor
            if not record.email:
                raise UserError("El estudiante no tiene un correo electrónico registrado.")

            # Preparar datos del correo
            subject = f"Actualización de Solicitud de Práctica: {record.name}"
            body = f"""
                        <p>Estimado/a {record.name},</p>
                        <p>Su solicitud de práctica ha sido actualizada al estado : <b>{dict(self._fields['state'].selection).get(record.state)}</b>.</p>
                        <p>Por favor contacta a tu tutor/a ({record.tutor_id.name}) para mas detalles.</p>
                        <p>Atentamente,<br>Tu Equipo</p>
                    """
            email_values_student = {
                'subject': subject,
                'body_html': body,
                'email_to': record.email,
            }

            self.env['mail.mail'].create(email_values_student).send()

            if record.tutor_id and not record.tutor_id.email:
                raise UserError("El tutor no tiene un correo electrónico registrado.")
            else:
                email_values_tutor = {
                    'subject': subject,
                    'body_html': f"""
                                                <p>Estimado/a {record.tutor_id.name},</p>
                                                <p>La solicitud de práctica para <b>{record.name}</b> ha sido actualizado al estado: <b>{dict(self._fields['state'].selection).get(record.state)}</b>.</p>
                                                <p>Revise los detalles y ayude según sea necesario.</p>
                                                <p>Atentamente,<br>Tu Equipo</p>
                                            """,
                    'email_to': record.tutor_id.email,
                }

                # Enviar correos

                self.env['mail.mail'].create(email_values_tutor).send()

    @api.depends('checklist_ids.is_completed', 'checklist_ids.is_mandatory')
    def _compute_checklist_completed(self):
        for record in self:
            if len(record.checklist_ids)>0:
                record.checklist_completed = all(
                    item.is_completed or not item.is_mandatory for item in record.checklist_ids
                )
            else:
                record.checklist_completed = False


    def generate_checklist(self):
        """
        Generate checklist items for the request based on the expected activities/documents.
        """
        for record in self:
            # Clear existing checklist items
            record.checklist_ids.unlink()

            # Fetch expected items for the practice center type
            expected_items = self.env['practice.center.expected'].search([
                ('practice_center_type_id', '=', record.practice_center_type_id.id)
            ])

            # Create checklist items
            for item in expected_items:
                self.env['practice.request.checklist'].create({
                    'name': item.name,
                    'expected_id': item.id,
                    'practice_request_id': record.id,
                    'sequence': item.sequence,
                })

    def action_mark_as_done(self):
        for record in self:
            if not record.checklist_completed:
                raise UserError("Debe completar todos los elementos obligatorios de la lista de verificación antes de finalizar.")

    def name_get(self):
        res = []
        for record in self:
            name = 'Solcitud de Practicas No. %s - %s' % (record.id, record.name)
            res.append((record.id, name))
        return res

    @api.depends('sign_request_specific_agrement_id', 'sign_request_framework_agrement_id')
    def _status_sign(self):
        # sign_framework = self.env['sign.request'].search([('id', '=', self.sign_request_framework_agrement_id)])
        # sign_specific = self.env['sign.request'].search([('id', '=', self.sign_request_specific_agrement_id)])
        # if len(sign_specific)> 0 and len(sign_framework) > 0:
        #     if sign_specific.state == "sent":
        #         self.status_sign_specific = 'Signatures Pending'
        #     if sign_framework.state == "sent":
        #         self.status_sign_framework = 'Signatures Pending'
        #     if sign_specific.state == "signed":
        #         self.status_sign_specific = 'Fully Signed'
        #     if sign_framework.state == "signed":
        #         self.status_sign_framework = 'Fully Signed'
        #     if sign_specific.state == "cancelled":
        #         self.status_sign_specific = 'cancelled'
        #     if sign_framework.state == "cancelled":
        #         self.status_sign_framework = 'cancelled'
        # else:
        #     self.status_sign_specific = 'Signatures Pending'
        #     self.status_sign_framework = 'Signatures Pending'
        # # Si ambos están "Fully Signed", cambiar el estado a "progress"

        # if self.status_sign_specific == 'Fully Signed' and self.status_sign_framework == 'Fully Signed' and self.state == "approved":
        #     self.state = 'progress'

        for record in self:
            specific = self.env['sign.request'].browse(record.sign_request_specific_agrement_id)
            framework = self.env['sign.request'].browse(record.sign_request_framework_agrement_id)

            # _logger.info("222"*200, specific, framework)

            # Inicializar estados en "Signatures Pending"
            record.status_sign_specific = 'Signatures Pending'
            record.status_sign_framework = 'Signatures Pending'

            # Evaluar estados si existen los registros
            if specific.exists():
                if specific.state == "sent":
                    record.status_sign_specific = 'Signatures Pending'
                elif specific.state == "signed":
                    record.status_sign_specific = 'Fully Signed'
                elif specific.state == "cancelled":
                    record.status_sign_specific = 'cancelled'

            if framework.exists():
                if framework.state == "sent":
                    record.status_sign_framework = 'Signatures Pending'
                elif framework.state == "signed":
                    record.status_sign_framework = 'Fully Signed'
                elif framework.state == "cancelled":
                    record.status_sign_framework = 'cancelled'

            # Si ambos documentos están firmados y el estado es "approved", cambiar a "progress"
            if (record.status_sign_specific == 'Fully Signed' and
                record.status_sign_framework == 'Fully Signed' and
                record.state == "approved"):
                record.state = 'progress'

    @api.depends('practice_center_type_id', 'course_id')
    def _compute_available_practice_centers(self):
        """
        Compute the available practice centers based on the selected
        practice_center_type_id and course_id.
        """
        for record in self:
            if record.practice_center_type_id and record.course_id:
                # Buscar centros de práctica que cumplan los criterios
                centers = self.env['practice.center'].search([
                    ('type_ids', 'in', record.practice_center_type_id.id),
                    ('status_form_center', '=', 'generated'),
                ])
                record.available_practice_centers_ids = centers
            else:
                # Si no se selecciona tipo o curso, no hay centros disponibles
                record.available_practice_centers_ids = False

    # Métodos de acción
    def action_submit(self):
        self.send_practice_center_assignment_email()
        self.state = 'assigned'

    def action_approve(self):
        self.state = 'approved'

    def action_reject(self):
        self.state = 'rejected'

    def action_draft(self):
        self.state = 'draft'

    def action_progress(self):
        self.state = 'progress'

    def action_end(self):
        self.action_mark_as_done()
        self.state = 'end'

    def send_practice_center_assignment_email(self):
        for request in self:
            # Verificar si se ha asignado un centro de práctica
            if not request.practice_center_id:
                raise UserError("No se ha asignado un centro de práctica a esta solicitud.")

            # Generar la URL del portal para la aceptación de la asignación
            portal_link = f"{self.env['ir.config_parameter'].sudo().get_param('web.base.url')}{'/my/practice_requests2'}"

            # Contenido del correo
            subject = "Asignación de Centro de Prácticas"
            body = f"""
                    <p>Estimado/a <strong>{request.name}</strong>,</p>

                    <p>Nos complace informarte que se te ha asignado un <strong>centro de prácticas</strong> para el curso <em>"{request.course_id.course_id.name}"</em>.</p>

                    <p>El centro asignado es: <strong>{request.practice_center_id.official_name}</strong>.</p>

                    <p>Para aceptar esta asignación, por favor ingresa al siguiente enlace en tu portal de estudiante:</p>
                    <p style="text-align: center;">
                        <a href="{portal_link}" style="padding: 10px 20px; background-color: #007bff; color: #fff; text-decoration: none; border-radius: 5px;">
                            <strong>Aceptar Asignación de Centro</strong>
                        </a>
                    </p>

                    <p>Una vez ingreses al portal, podrás <strong>confirmar tu asignación</strong> y coordinar los detalles con el centro de prácticas.</p>

                    <p>Si tienes alguna duda o necesitas más información, no dudes en contactarnos.</p>

                    <p>Saludos cordiales,</p>
                    <p>El equipo de prácticas.</p>
                """

            # Enviar el correo
            mail_values = {
                'subject': subject,
                'body_html': body,
                'email_to': request.email,
            }

            mail = self.env['mail.mail'].create(mail_values)
            mail.send()
            return True

    def email_framework_agreement(self):
        self.ensure_one()
        # try:

        REPORT_ID = 'isep_practices_2.report_anexo_one_print'
        report = self.env.ref(REPORT_ID)

        pdf_content, _ = self.env['ir.actions.report']._render_qweb_pdf(
            'isep_practices_2.report_anexo_one_print', [self.id])

        b64_pdf = base64.b64encode(pdf_content)
        ATTACHMENT_NAME = f"acuerdo_de_condiciones_de_resguardo_{self.practice_center_id.name}_{self.id}.pdf"
        subject = "Solicitud de Firma en Acuerdo de Condiciones " + ATTACHMENT_NAME
        pdfstring = f"data:application/pdf;base64,{b64_pdf.decode('utf-8')}"

        attachment = self.env['ir.attachment'].create({
            'name': ATTACHMENT_NAME,
            'type': 'binary',
            'datas': b64_pdf,
            'res_model': 'practice.request',
            'res_id': self.id,
            'mimetype': 'application/pdf'
        })

        sign_template = self.env['sign.template'].create({
            'attachment_id': attachment.id,
            'name': ATTACHMENT_NAME,
        })

        if sign_template:
            sign_items = {
                '-1': {
                    'required': True,
                    'responsible_id': 1,
                    'page': 2,
                    'type_id': 1,
                    'posX': 0.179,
                    'posY': 0.767,
                    'width': 0.159,
                    'height': 0.031
                },

                '-2': {
                    'required': False,
                    'responsible_id': 1,
                    'page': 2,
                    'type_id': 9,
                    'posX': 0.342,
                    'posY': 0.837,
                    'width': 0.028,
                    'height': 0.025
                },
                '-3': {
                    'required': False,
                    'responsible_id': 1,
                    'page': 2,
                    'type_id': 9,
                    'posX': 0.676,
                    'posY': 0.837,
                    'width': 0.028,
                    'height': 0.025
                }
            }

            sign_template.update_from_pdfviewer(sign_items=sign_items)

            actual_partner_ids = [self.course_id.student_id.partner_id.id]

            sign_request_items = []
            for idx, sign_item in enumerate(sign_template.sign_item_ids):
                if idx < len(actual_partner_ids):
                    partner_id = actual_partner_ids[idx]
                    role_id = sign_item.responsible_id.id

                    sign_request_items.append((0, 0, {
                        'partner_id': partner_id,
                        'role_id': role_id
                    }))

            if sign_request_items:
                sign_request = self.env['sign.request'].create({
                    'subject': subject,
                    'template_id': sign_template.id,
                    'reference': ATTACHMENT_NAME,
                    'request_item_ids': sign_request_items
                })

                if sign_request:
                    self.sign_request_framework_agrement_id = sign_request.id
                    sign_request.send_signature_accesses()
                    return True
        return False
        # except Exception as e:
        #     return False

    def email_specific_agreement(self):
        self.ensure_one()
        # try:

        REPORT_ID = 'isep_practices_2.report_specific_agreement'

        report = self.env.ref(REPORT_ID)

        pdf_content, _ = self.env['ir.actions.report']._render_qweb_pdf(
            'isep_practices_2.report_specific_agreement', [self.id])
        b64_pdf = base64.b64encode(pdf_content)
        ATTACHMENT_NAME = f"convenio_especifico_{self.name}_{self.id}.pdf"
        subject = "Solicitud de Firma en " + ATTACHMENT_NAME
        pdfstring = f"data:application/pdf;base64,{b64_pdf.decode('utf-8')}"

        attachment = self.env['ir.attachment'].create({
            'name': ATTACHMENT_NAME,
            'type': 'binary',
            'datas': b64_pdf,
            'res_model': 'practice.request',
            'res_id': self.id,
            'mimetype': 'application/pdf'
        })

        sign_template = self.env['sign.template'].create({
            'attachment_id': attachment.id,
            'name': ATTACHMENT_NAME,
        })

        if sign_template:
            sign_items = {
                '-0': {'required': True, 'responsible_id': 10, 'page': 2, 'type_id': 1, 'posX': 0.169,
                       'posY': 0.566, 'width': 0.200, 'height': 0.050},
                '-1': {'required': True, 'responsible_id': 1, 'page': 2, 'type_id': 1, 'posX': 0.197,
                       'posY': 0.519, 'width': 0.200, 'height': 0.050}
            }

            sign_template.update_from_pdfviewer(sign_items=sign_items)

            actual_partner_ids = [self.course_id.student_id.partner_id.id]

            sign_request_items = []
            for idx, sign_item in enumerate(sign_template.sign_item_ids):
                if idx < len(actual_partner_ids):
                    partner_id = actual_partner_ids[idx]
                    role_id = sign_item.responsible_id.id

                    sign_request_items.append((0, 0, {
                        'partner_id': partner_id,
                        'role_id': role_id
                    }))

            if sign_request_items:
                sign_request = self.env['sign.request'].create({
                    'subject': subject,
                    'template_id': sign_template.id,
                    'reference': ATTACHMENT_NAME,
                    'request_item_ids': sign_request_items
                })

                if sign_request:
                    self.sign_request_specific_agrement_id = sign_request.id
                    sign_request.send_signature_accesses()
                    return True
        return False
        # except Exception as e:
        #     return False

    def action_create_signature_request(self):
        practice = self.search([('id', '=', self.id)])
        if not practice.final_date:
            raise UserError(_("No ha definido una fecha final para las practicas"))
        if not practice.start_date:
            raise UserError(_("No ha definido una fecha inicial para las practicas"))

        if not practice.sign_request_specific_agrement_id and not practice.sign_request_framework_agrement_id:
            framework_success = practice.email_framework_agreement()
            specific_success = practice.email_specific_agreement()

            if framework_success and specific_success:
                practice.write({'email_send': 'framework_specific'})
            else:
                practice.write({'email_send': 'not_send'})
                raise UserError(_(
                    "Ha ocurrido un error al momento de generar la petición de firma, contacte con el administrador del sistema."))
        else:
            raise UserError(_("No se puede enviar el convenio a firmar más de una vez"))


    def generate_checklist_cron(self):

        # for record in self:
        #     # Clear existing checklist items
        #     record.checklist_ids.unlink()

        #     # Fetch expected items for the practice center type
        #     expected_items = self.env['practice.center.expected'].search([
        #         ('practice_center_type_id', '=', record.practice_center_type_id.id)
        #     ])

        #     # Create checklist items
        #     for item in expected_items:
        #         self.env['practice.request.checklist'].create({
        #             'name': item.name,
        #             'expected_id': item.id,
        #             'practice_request_id': record.id,
        #             'sequence': item.sequence,
        #         })

        requests = self.search([])  # Obtener todos los registros del modelo
        for record in requests:
            # Eliminar elementos de checklist existentes
            record.checklist_ids.unlink()

            # Obtener los elementos esperados según el tipo de centro de práctica
            expected_items = self.env['practice.center.expected'].search([
                ('practice_center_type_id', '=', record.practice_center_type_id.id)
            ])

            # Crear nuevos elementos de checklist
            for item in expected_items:
                self.env['practice.request.checklist'].create({
                    'name': item.name,
                    'expected_id': item.id,
                    'practice_request_id': record.id,
                    'sequence': item.sequence,
                })


    def cron_send_signature_request(self):
        """Cron para enviar la solicitud de firma automáticamente en estado aprobado"""
        approved_practices = self.search([('state', '=', 'approved')])

        for practice in approved_practices:
            try:
                practice.action_create_signature_request()
            except UserError as e:
                # Puedes registrar errores en el log del servidor
                _logger.error(f"Error en el cron de firma: {e}")

    def cron_request_approved_to_progress(self):
        approved_practices = self.search([
            ('state', '=', 'approved'),
            ('sign_request_specific_agrement_id', '!=', False),
            ('sign_request_framework_agrement_id', '!=', False)
        ])

        for practice in approved_practices:
            practice.write({'state': 'progress'})



class fccDocumentsIrAttachment(models.Model):
    _inherit = 'ir.attachment'

    practice_request_id = fields.Many2one(
        'practice.request',
        string="Practice Request",
        ondelete="cascade"

    )

    document_type = fields.Selection(
        [('agreement', 'Agreement'),
         ('certificate', 'Certificate'),
         ('report', 'Report'),
         ('other', 'Other')],
        string='Document Type',

        tracking=True
    )
