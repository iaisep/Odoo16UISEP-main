from odoo import models, fields, api
from datetime import datetime
from dateutil.relativedelta import relativedelta

class AppisepGradebookSummary(models.Model):
    _name = 'appisep.gradebook.summary'
    _description = 'Gradebook Summary'

    company_id = fields.Many2one("res.company", string="Company", default=lambda self: self.env.company, help="Related Company")
    student_id = fields.Many2one('res.partner', string='Estudiante')
    course_id = fields.Many2one('op.course', string='Curso')
    batch_id = fields.Many2one('op.batch', string='Lote')
    admision_id = fields.Many2one('op.admission', string='Admision')
    total_marks = fields.Float(string='Total Marks')
    description = fields.Char(string='Descripción')
    mail_send = fields.Boolean(string='Correo enviado', default=False)


    def determine_current_quarter(self):
        try:
            start_date = self.batch_id.start_date
            end_date = self.batch_id.end_date
            final_notes = []
            current_quarter = None

            if not start_date or not end_date:
                return final_notes

            current_date = datetime.now().date()
            
            if start_date <= current_date <= end_date:
                quarters = []
                current_start = start_date
                counter = 1

                while current_start <= end_date:
                    q_end = current_start + relativedelta(months=4, days=-1)

                    if q_end > end_date:
                        q_end = end_date
                    
                    quarters.append({
                        'number': counter,
                        'start': current_start,
                        'end': q_end,
                        'active': q_end >= current_date 
                    })
                    
                    current_start = q_end + relativedelta(days=1)
                    counter += 1

                for q in quarters:
                    if q['start'] <= current_date <= q['end']:
                        current_quarter = q
                        break
                #print("//////////////////////////",quarters)
                if current_quarter:
                    description = f"Cuatrimestre {current_quarter['number']}: {current_quarter['start'].strftime('%d/%m/%Y')} - {current_quarter['end'].strftime('%d/%m/%Y')}"
                    
                    slide_channels = self.env['slide.channel.partner'].search([
                        ('active', '=', True),
                        ('partner_id', '=', self.student_id.id),
                        ('op_subject_id.subject_type', '=', 'compulsory'),
                        ('batch_id', '=', self.batch_id.id),
                        ('write_date', '>=', current_quarter['start']),
                        ('write_date', '<=', current_quarter['end'])
                    ])
                    
                    current_quarter_ids = slide_channels.op_subject_id.ids
                    
                    if current_quarter_ids:
                        subject_notes = self.env['app.gradebook.subject'].search([
                            ('op_subject_id', 'in', current_quarter_ids),
                            ('admission_id', '=', self.admision_id.id),
                            ('partner_id', '=', self.student_id.id)
                        ])                    
                        final_notes = subject_notes.mapped('final_subject_note')
                        average = sum(final_notes) / len(final_notes) if final_notes else 0.0
                        self.write({
                            'total_marks': average,
                            'description': description,
                            'mail_send' : False
                        })
            
            return final_notes

        except Exception as e:
            _logger.error(f"Error en registro {self.id}: {str(e)}")
            return []

    def _compute_total_marks_cron(self):
        try:
            records = self.env['appisep.gradebook.summary'].search([
                ('batch_id', '!=', False),
                ('student_id', '!=', False),
                ('admision_id', '!=', False)
            ], order='id')
            
            batch_size = 100
            for i in range(0, len(records), batch_size):
                batch = records[i:i+batch_size]
                for record in batch:
                    try:
                        with self.env.cr.savepoint():
                            record.sudo().determine_current_quarter()
                    except Exception as e:
                        _logger.error(f"Error procesando registro cuatrimestre report {record.id}: {str(e)}")
                        continue
                self.env.cr.commit()                 
        except Exception as cron_error:
            _logger.error(f"Error general en cron cuatrimestres report: {str(cron_error)}")        
        return True
    
    
    def action_print_certificate_recognition(self):
        for rec in self:
            return rec.env.ref('isep_gradebook.action_recognition_certificate').report_action(self)

    def action_send_recognition(self):   
        for rec in self:
            if rec.mail_send == False:
                ctx = {}
                email_list = rec.student_id.email
                if email_list:
                    ctx['email_to'] = email_list
                    ctx['email_from'] = rec.env.user.partner_id.email
                    ctx['send_email'] = True
                    ctx['attendee'] = rec.student_id.name
                    template = rec.env.ref('isep_gradebook.email_template_recognition_certificate')
                    template.with_context(ctx).send_mail(rec.id, force_send=True, raise_exception=False)
                    rec.write({'mail_send': True})
    

class OpAdmission(models.Model):
    _inherit = 'op.admission'

    def write(self, vals):
        original_states = {record.id: record.state for record in self}
        result = super(OpAdmission, self).write(vals)        
        for record in self:
            original_state = original_states.get(record.id)
            new_state = record.state
            if original_state == 'done' and new_state != 'done':
                summary = self.env['appisep.gradebook.summary'].search([
                    ('admision_id', '=', record.id)
                ])
                if summary:
                    summary.sudo().unlink()

            if new_state == 'done' and original_state != 'done':
                if record.student_id.status_student == 'valid':
                    existing = self.env['appisep.gradebook.summary'].search([
                        ('admision_id', '=', record.id)
                    ], limit=1)
                    if not existing:
                        self.env['appisep.gradebook.summary'].sudo().create({
                            'student_id': record.partner_id.id,
                            'course_id': record.course_id.id,
                            'batch_id': record.batch_id.id,
                            'admision_id': record.id,
                            'total_marks': 0,
                        })
        
        return result

    def cron_create_student_gradebook_summary(self):
        valid_done_admissions = self.search([
            ('state', '=', 'done'),
            ('student_id.status_student', '=', 'valid')
        ])
        existing_admission_ids = self.env['appisep.gradebook.summary'].search([
            ('admision_id', 'in', valid_done_admissions.ids)
        ]).mapped('admision_id.id')

        new_admissions = valid_done_admissions.filtered(
            lambda a: a.id not in existing_admission_ids
        )        
        if new_admissions:
            summaries = []
            for admission in new_admissions:
                summaries.append({
                    'student_id': admission.partner_id.id,
                    'course_id': admission.course_id.id,
                    'batch_id': admission.batch_id.id,
                    'admision_id': admission.id,
                    'total_marks': 0,
                })
            self.env['appisep.gradebook.summary'].sudo().create(summaries)