# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, date
import base64

_logger = logging.getLogger(__name__)


class PracticePractice(models.Model):
    _name = 'practice.practice'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'PracticePractice'
    _rec_name = 'op_admission_id'

    weekly_hours = fields.Float(string='Weekly Hours', compute="_compute_weekly_hours")
    total_hours = fields.Float(string='Total Hours', compute="_compute_total_hours")
    start_date = fields.Date(string='Start Date')
    final_date = fields.Date(string='Final Date')
    practice_temary_id = fields.Many2one('practice.temary', string='Temary')
    tutor_id = fields.Many2one('res.partner', string='Tutor')
    op_student_id = fields.Many2one('op.student', string='Student')
    op_admission_id = fields.Many2one("op.admission", 'Admission')
    status_phase = fields.Selection([
        ('in progress', 'En Espera'),
        ('started', 'Iniciada'),
        ('pending by rating', 'Pendiente por Nota'),
        ('finished', 'Finalizada'), ], 'Phase', track_visibility='onchange', default='in progress')
    email_send = fields.Selection([
        ('framework_specific', 'Convenio Marco y Convenio Especifico enviados por correo'),
        ('not_send', 'Convenios no enviados'), ], 'Status Agreement', track_visibility='onchange')
    status_sign_specific = fields.Selection([
        ('Signatures Pending', 'Firma en Trámite'),
        ('Fully Signed', 'Totalmente Firmado'),
        ('cancelled', 'Cancelado'), ], 'Status Sign Specific Agreement', track_visibility='onchange', compute="_status_sign")
    status_sign_framework = fields.Selection([
        ('Signatures Pending', 'Firma en Trámite'),
        ('Fully Signed', 'Totalmente Firmado'),
        ('cancelled', 'Cancelado'), ], 'Status Sign Framework Agreement', track_visibility='onchange', compute="_status_sign")
    op_course_id = fields.Many2one('op.course', string='Course', related='op_admission_id.course_id')
    remuneration_center = fields.Float(string='Remuneration Center')
    center_id = fields.Many2one('res.partner', string='Center', domain="[('center', '=', True)]")
    payment_center = fields.Boolean(string='Payment to the Center', default=False)
    morning = fields.Boolean(string='Morning', default=False)
    afternoon = fields.Boolean(string='Afternoon', default=False)
    sign_request_specific_agrement_id = fields.Integer()
    sign_request_framework_agrement_id = fields.Integer()
    active = fields.Boolean(default=True)
    sign_id = fields.Many2one('sign.template', string="framework agreement template", copy=False)


    _sql_constraints = [
        ('check_dates',
         'CHECK (start_date <= final_date)',
         'Fecha de inicio no debe ser menor a fecha final.'),
    ]

    id_sign_request_framework = 0
    id_sign_request_specific = 0


    
    @api.depends('sign_request_specific_agrement_id', 'sign_request_framework_agrement_id')
    def _status_sign(self):
        sign_framework = self.env['sign.request'].search([('id', '=', self.sign_request_framework_agrement_id)])
        sign_specific = self.env['sign.request'].search([('id', '=', self.sign_request_specific_agrement_id)])
        if len(sign_specific) and len(sign_framework):
            if sign_specific.state == "sent":
                self.status_sign_specific = 'Signatures Pending'
            if sign_framework.state == "sent":
                self.status_sign_framework = 'Signatures Pending'
            if sign_specific.state == "signed":
                self.status_sign_specific = 'Fully Signed'
            if sign_framework.state == "signed":
                self.status_sign_framework = 'Fully Signed'
            if sign_specific.state == "cancelled":
                self.status_sign_specific = 'cancelled'
            if sign_framework.state == "cancelled":
                self.status_sign_framework = 'cancelled'
        else:
            self.status_sign_specific = 'Signatures Pending'
            self.status_sign_framework = 'Signatures Pending'

    
    @api.onchange('center_id', 'op_admission_id')
    def filterContactByCenter(self):
        course = self.env['practice.center.course'].search([('op_course_id', '=', self.op_admission_id.course_id.id)])
        course_center = [courses.partner_id.id for courses in course]
        return {'domain': {'center_id': [('center', '=', True), ('id', 'in', course_center)]}}


    @api.onchange('center_id', 'op_admission_id', 'morning', 'afternoon')
    def filterCenterByTurn(self):
        turn_morning = self.env['practice.schedule'].search([('turn', '=', 'morning')])
        turn_schedule_morning = [turns.id for turns in turn_morning]
        turn_afternoon = self.env['practice.schedule'].search([('turn', '=', 'afternoon')])
        turn_schedule_afternoon = [turns.id for turns in turn_afternoon]
        turn_both = self.env['practice.schedule'].search([('turn', '=', 'both')])
        turn_schedule_both = [turns.id for turns in turn_both]

        if self.morning and self.afternoon:
            return {'domain': {'center_id': [('practice_schedule_id', 'in', turn_schedule_both)]}}
        if self.morning:
            return {'domain': {'center_id': [('practice_schedule_id', 'in', turn_schedule_morning)]}}
        if self.afternoon:
            return {'domain': {'center_id': [('practice_schedule_id', 'in', turn_schedule_afternoon)]}}
        else:
            course = self.env['practice.center.course'].search(
                [('op_course_id', '=', self.op_admission_id.course_id.id)])
            course_center = [courses.partner_id.id for courses in course]
            return {'domain': {'center_id': [('center', '=', True), ('id', 'in', course_center)]}}


    
    @api.onchange('tutor_id', 'center_id', 'op_admission_id')
    def filterContactByTutor(self):
        center = self.env['practice.center.tutor'].search([('partner_id', '=', self.center_id.id)])
        center_tutor = [centers.tutor_id.id for centers in center]
        course = self.env['practice.tutor.course'].search([('op_course_id', '=', self.op_admission_id.course_id.id)])
        tutor_course = [courses.partner_id.id for courses in course]
        return {'domain': {'tutor_id': [('tutor', '=', True), ('id', 'in', center_tutor), ('id', 'in', tutor_course)]}}


    
    @api.onchange('op_admission_id', 'op_student_id')
    def filterAdmisionByStudent(self):
        return {'domain': {'op_admission_id': [('student_id', '=', self.op_student_id.id)]}}


    def getDay(self):
        if self.start_date and self.final_date:
            my_time = datetime.min.time()
            start_date_datetime = datetime.combine(self.start_date, my_time)
            final_date_datetime = datetime.combine(self.final_date, my_time)
            start_date_new = datetime.strptime(str(start_date_datetime), "%Y-%m-%d %H:%M:%S").date()
            final_date_new = datetime.strptime(str(final_date_datetime), "%Y-%m-%d %H:%M:%S").date()
            result_date = final_date_new - start_date_new
            days = str(result_date).replace(' days, 0:00:00', '')
            weeks = int(days) // 7
            return weeks



    @api.depends('op_admission_id.batch_id.code')
    def _compute_total_hours(self):
        for record in self:
            op_course = self.env['op.course'].search([('id', '=', record.op_course_id.id)])
            op_course_subject_rel = op_course.subject_ids
            record.total_hours = 0
            for op_course_subject in op_course_subject_rel:
                if 'práctica' in str(op_course_subject.name).lower():
                    record.total_hours = op_course_subject.credit_point
                    break

    @api.depends('start_date', 'final_date', 'total_hours')
    def _compute_weekly_hours(self):
        for record in self:
            if record.total_hours > 0 and record.start_date and record.final_date:
                for practice in record:
                    practice.weekly_hours = practice.total_hours / practice.getDay()
            else:
                record.weekly_hours = 0


    
    def email_framework_agreement(self):
        self.ensure_one()
        try:

            REPORT_ID = 'isep_practices.report_framework_agreement_template'
            report = self.env.ref(REPORT_ID)            
            
            pdf_content, _ = self.env['ir.actions.report']._render_qweb_pdf('isep_practices.report_framework_agreement_template', [self.id])

            b64_pdf = base64.b64encode(pdf_content)
            ATTACHMENT_NAME = f"convenio_marco_practicas_isep_y_{self.center_id.name}.pdf"
            pdfstring = f"data:application/pdf;base64,{b64_pdf.decode('utf-8')}"

            attachment = self.env['ir.attachment'].create({
                'name': ATTACHMENT_NAME,
                'type': 'binary',
                'datas': b64_pdf,
                'res_model': 'practice.practice',
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
                        'posX': 0.604,
                        'posY': 0.712,
                        'width': 0.200,
                        'height': 0.050
                    }
                }

                sign_template.update_from_pdfviewer(sign_items=sign_items)

                actual_partner_ids = [self.op_student_id.partner_id.id]

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
                        'template_id': sign_template.id,
                        'reference': ATTACHMENT_NAME,
                        'request_item_ids': sign_request_items
                    })

                    if sign_request:
                        self.sign_request_framework_agrement_id = sign_request.id
                        sign_request.send_signature_accesses()
                        return True
            return False
        except Exception as e:
            return False




    def email_specific_agreement(self):
        self.ensure_one()
        try:

            REPORT_ID = 'isep_practices.report_specific_agreement_template'
            report = self.env.ref(REPORT_ID)

            pdf_content, _ = self.env['ir.actions.report']._render_qweb_pdf('isep_practices.report_specific_agreement_template', [self.id])
            b64_pdf = base64.b64encode(pdf_content)
            ATTACHMENT_NAME = f"convenio_especifico_{self.op_student_id.name}.pdf"
            pdfstring = f"data:application/pdf;base64,{b64_pdf.decode('utf-8')}"

            attachment = self.env['ir.attachment'].create({
                'name': ATTACHMENT_NAME,
                'type': 'binary',
                'datas': b64_pdf,
                'res_model': 'practice.practice',
                'res_id': self.id,
                'mimetype': 'application/pdf'
            })

            sign_template = self.env['sign.template'].create({
                'attachment_id': attachment.id,
                'name': ATTACHMENT_NAME,
            })

            if sign_template:
                sign_items = {
                    '-0': {'required': True, 'responsible_id': 10, 'page': 2, 'type_id': 1, 'posX': 0.169, 'posY': 0.566, 'width': 0.200, 'height': 0.050},
                    '-1': {'required': True, 'responsible_id': 1, 'page': 2, 'type_id': 1, 'posX': 0.150, 'posY': 0.480, 'width': 0.200, 'height': 0.050}
                }

                sign_template.update_from_pdfviewer(sign_items=sign_items)

                actual_partner_ids = [self.op_student_id.partner_id.id]

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
                        'template_id': sign_template.id,
                        'reference': ATTACHMENT_NAME,
                        'request_item_ids': sign_request_items
                    })

                    if sign_request:
                        self.sign_request_specific_agrement_id = sign_request.id
                        sign_request.send_signature_accesses()
                        return True
            return False
        except Exception as e:
            return False

    
    def action_create_signature_request(self):
        practice = self.search([('id', '=', self.id)])

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


    def start_practice(self):
        practices = self.search([('start_date', '=', date.today())])
        if len(practices):
            for practice in practices:
                value = {'status_phase': 'started'}
                practice.write(value)
                logger.info('****************************************')
                logger.info('* UPDATE PHASE OF PRACTICE TO STARTED  *')
                logger.info('****************************************')


    
    def finish_practice(self):
        practices = self.search([('final_date', '<=', date.today())])
        if len(practices):
            print(practices)
            for practice in practices:
                if practice.status_phase != 'finished':
                    op_exam_attendees = self.env['op.exam.attendees'].search(
                        [('student_id', '=', practice.op_student_id.id),
                         ('course_id', '=', practice.op_admission_id.course_id.id),
                         ('batch_id', '=', practice.op_admission_id.batch_id.id)])
                    if len(op_exam_attendees):
                        for op_exam_attendee in op_exam_attendees:
                            print(op_exam_attendee)
                            op_exam = self.env['op.exam'].search(
                                [('id', '=', op_exam_attendee.exam_id.id)])
                            if len(op_exam):
                                print(op_exam)
                                if 'práctica' in str(op_exam.subject_id.name).lower() or 'practica' in str(
                                        op_exam.subject_id.name).lower():
                                    if op_exam_attendee.marks > 0:

                                        value = {'status_phase': 'finished'}
                                        practice.write(value)
                                        logger.info('****************************************')
                                        logger.info('* UPDATE PHASE OF PRACTICE TO FINISHED *')
                                        logger.info('****************************************')
                                    else:
                                        if practice.status_phase != 'pending by rating':
                                            value = {'status_phase': 'pending by rating'}
                                            practice.write(value)
                                            logger.info('*************************************************')
                                            logger.info('* UPDATE PHASE OF PRACTICE TO PENDING BY RATING *')
                                            logger.info('*************************************************')