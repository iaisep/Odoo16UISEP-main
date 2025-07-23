# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError
import logging
from babel.dates import format_date

logger = logging.getLogger(__name__)


class Struct:
    def __init__(self, **entries):
        self.__dict__.update(entries)


class DiplomasCertifies(models.TransientModel):
    _name = 'diplomas.certifies'

    def _set_student(self):
        student_id = self.env.context.get('active_id', []) or []
        student = self.env['op.student'].search([('id', '=', student_id)])
        return [('id', '=', student.id)]

    def _set_batch_ids(self):
        student_id = self.env.context.get('active_id', False) 
        student_course_ids = self.env['op.student.course'].search([('student_id', '=', student_id)])
        batch_ids = student_course_ids.mapped('batch_id')
        return [('id', 'in', batch_ids.ids)]

    def _set_report_domain(self):
        reports = self.env['ir.actions.report'].search([('report_name', 'like', '%isep_openeducat_reports%')])
        return [('id','in',reports.ids)]

    def _get_student(self):
        student_id = self.env.context.get('active_ids', []) or []
        logger.info(student_id)
        return self.env['op.student'].search([('id', 'in', student_id)])

    student_id = fields.Many2one('op.student', string="Student",
                                 default=_get_student, domain=_set_student,
                                 required=True)
    course_id = fields.Many2one('op.course', string="Curso")
    file_id = fields.Many2one('ir.actions.report', string="Documento",
                              domain=_set_report_domain, required=True)
    batch_id = fields.Many2many('op.batch', string="Lote",
                               domain=_set_batch_ids, required=True)
    admission_id = fields.Many2one('op.admission', string="Admission")

    @api.onchange('student_id')
    def _onchange_student(self):
        logger.info(self.student_id.course_detail_ids.ids)
        course_list = []
        for student_course in self.student_id.course_detail_ids:
            course_list.append(student_course.course_id.id)

        logger.info(course_list)
        for rec in self:
            return {'domain': {
                'course_id': [(
                    'id',
                    'in',
                    course_list)],
                }}

    @api.onchange('course_id')
    def _onchange_course(self):
        logger.info(self.student_id.course_detail_ids.ids)

        courses = self.student_id.course_detail_ids
        admissions = self.student_id.admission_ids
        for rec in self:
            for batch in courses:
                if batch.course_id == self.course_id:
                    rec.batch_id = batch.batch_id

            for admission in admissions:
                if admission.batch_id == self.batch_id:
                    rec.admission_id = admission.id

            print(rec.admission_id)
            print(rec.batch_id)
            print(rec.batch_id.end_date)

    def get_data(self):
        admissions = self.env['op.student.course'].search([('student_id','=',self.student_id.id),('batch_id','=',self.batch_id.id)])
        report_name = str(self.file_id.report_name)
        start_date = self.batch_id[0].start_date.strftime('%d-%m-%Y')
        end_date = self.batch_id[0].end_date.strftime('%d-%m-%Y')

        data = {}
        student = self.student_id
        current_date = fields.Date.today()
        date_str = format_date(current_date, format='d MMMM y', locale='es_MX')
        data.update({
                'admissions': admissions,
                'batch_id': self.batch_id.id,
                'student_ids': student.ids,
                'doc_model': 'op.student',  # Odoo model name you're working with
        })
        return data

    def print_diploma_certify(self):
        options=self.get_data()
        report_id = self.env['ir.actions.report'].sudo().search([('id','=',self.file_id.id)])
        res = report_id.with_context(disable_attachment= True).report_action(self, data=options)
        user_id = self.env.user 
        student_id = self.student_id
        certificate_log = self.env['certificate.log'].sudo()
        log_vals = {
                    'date':fields.Datetime.now(),
                    'certificate_name':report_id.display_name,
                    'user_id': user_id.id,
                    'student_id': student_id.id,
                   }
        certificate_log.create(log_vals)

        return res

    def send_by_email(self):
         
        check_send = self.file_id.check_web_available(self.student_id, self.batch_id)
        if check_send == True :
            import base64
            body_message = '''Diploma/Certificado de %s
            ''' % self.student_id.partner_id.name
            subject = body_message
            report = self.print_diploma_certify()
            pdf, tipo = self.env['ir.actions.report'].sudo().search([(
                'id',
                '=',
                self.file_id.id)]).with_context(disable_attachment=True)._render_qweb_pdf(self.file_id.xml_id, data=self.get_data())
            pdf_content = base64.b64encode(pdf)
            attach = self.env['ir.attachment'].create({
                'name': self.file_id.name,
                'type': 'binary',
                'datas': pdf_content,
                'store_fname': self.file_id.name + '.pdf',
                'res_model': self.student_id._name,
                'res_id': self.student_id.id,
                'certificado_web': True,
                'certificado_gratuito': self.file_id.certificado_gratuito,
                'mimetype': 'application/pdf'
            })
            message = self.student_id.message_post(body=body_message, subject=subject,
                                                   attachment_ids=[att.id for att in attach], message_type='comment')
            mail_id = self.student_id.env['mail.mail'].create({'mail_message_id': message.id,
                                                               'body_html': body_message,
                                                               'recipient_ids': [(4, self.student_id.partner_id.id)],
                                                               'auto_delete': False,
                                                               'references': message.message_id,
                                                               'headers': "'{'X-Odoo-Objects': 'op.student-1'}'"})
            # mail_id = self.env['mail.mail'].search([])
            self.student_id.env['mail.notification'].create({
                'mail_message_id': message.id,
                'res_partner_id': self.student_id.partner_id.id,
                'is_read': True,
            })
            message.write({
                "subtype_id": 1,
                'partner_ids': [(4, self.student_id.partner_id.id)],
            })
        else:
            raise UserError(_('Reporte no cumple los requisitos: %s')% (check_send.get('error_message')) )
