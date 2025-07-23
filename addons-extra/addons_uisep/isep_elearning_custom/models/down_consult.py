import secrets
from odoo.exceptions import UserError 
from odoo import models, fields, api

class AdmissionDownconsultQuestion(models.Model):
    _name = 'admission.downconsult.question'
    _description = 'Down Consult question'
    _order= "sequence desc"

    name = fields.Char(string='Pregunta', required=True)
    active = fields.Boolean(string='Activo', default=True)
    sequence = fields.Integer(string='Secuencia', default=10)

class AdmissionDownconsult(models.Model):
    _name = 'admission.downconsult'
    _description = 'Down Consult'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    

    name = fields.Char(string='secuencia', required=False, related='student_id.display_name')
    company_id = fields.Many2one("res.company", string="Company", default=lambda self: self.env.company, help="Related Company")
    description = fields.Text(string='Comentario')
    admission_id = fields.Many2one('op.admission', string='Admisión', required=True)
    student_id = fields.Many2one(related='admission_id.student_id', string='Estudiante')
    course_id = fields.Many2one(related='admission_id.course_id', string='Curso')
    partner_id = fields.Many2one(related='admission_id.partner_id', string='Compañero')
    question_line_ids = fields.One2many(
            'admission.downconsult.line',
            'downconsult_id', index=True,
            string='Preguntas'
        )
    state = fields.Selection([('draft', 'En espera'), ('done', 'Contestado')], string='Estado', default='draft')
    access_token = fields.Char(string='Token de Acceso', copy=False)
    token_expiration = fields.Datetime(string='Expiración Token')

    def _generate_access_token(self):
        return secrets.token_hex(8)

    @api.model
    def create(self, vals):
        record = super().create(vals)
        record.access_token = record._generate_access_token()
        record.token_expiration = fields.Datetime.add(fields.Datetime.now(), days=7)
        questions = self.env['admission.downconsult.question'].search([])
        for question in questions:
            self.env['admission.downconsult.line'].create({
                'name': question.name,
                'rating': False,
                'downconsult_id': record.id
            })  
        record.action_send_down_mail()
        return record

    def action_mark_done(self):
        for record in self:
            record.state = 'done'

            message_lines = []
            message_lines.append("ENCUESTA LLENA DE EX-ESTUDIANTE DEL CURSO")
            for line in record.question_line_ids:
                message_lines.append("Pregunta: {} - Calificación: {}".format(line.name, line.rating))
            message_lines.append("*** Comentario adicional: {}".format(record.description or "Sin comentarios adicionales"))
            message_body = "<br/>".join(message_lines)
            record.admission_id.message_post(body=message_body)

    def action_print_report_donw(self):
        return self.env.ref('isep_elearning_custom.action_report_down_adminsion').report_action(self)

    def action_send_down_mail(self):   
        for rec in self:
            ctx = {}
            email_list = rec.admission_id.email
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            survey_url = f"{base_url}/downconsult/survey/{rec.access_token}"
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            if email_list:
                ctx['email_to'] = email_list
                ctx['email_from'] = self.env.user.partner_id.email
                ctx['send_email'] = True
                ctx['attendee'] = rec.partner_id.name
                ctx['survey_url'] = survey_url
                template = self.env.ref('isep_elearning_custom.email_template_down_report')
                template.with_context(ctx).send_mail(self.id, force_send=True, raise_exception=False)
                

class AdmissionDownconsultLine(models.Model):
    _name = 'admission.downconsult.line'
    _description = 'Down Consult'

    name = fields.Char(string='Pregunta', required=True)
    downconsult_id = fields.Many2one(
        'admission.downconsult',
        string='Down Consult',ondelete="cascade", index=True
    )
    course_id = fields.Many2one(related='downconsult_id.course_id', string='Curso', store=True)
    batch_id = fields.Many2one(related='downconsult_id.admission_id.batch_id', string='Lote', store=True)
    rating = fields.Selection([
        ('malo', 'Malo'),
        ('regular', 'Regular'),
        ('bueno', 'Bueno'),
        ('excelente', 'Excelente')
    ], string='Calificación')