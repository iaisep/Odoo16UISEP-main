
from datetime import datetime

from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import date
import logging

_logger = logging.getLogger(__name__)




class OpAdmissionRegister(models.Model):
    _inherit = 'op.admission.register'


    product_id = fields.Many2one(
        'product.product', 'Course Fees', required=False,
        domain=[('type', '=', 'service')], readonly=True,
        states={'draft': [('readonly', False)]}, tracking=True)

class OpAdmission(models.Model):
    _inherit = 'op.admission'

    tutor_id = fields.Many2one('res.users', related="batch_id.tutor_id" , readonly=True, string="Tutor de Orientación" )
    professor_id = fields.Many2one('res.users', related="batch_id.professor_id" , readonly=True, string="Tutor de Académico" )
    teams_email = fields.Char(string="Correo Teams", compute="compute_teams_email", store=True )
    teams_email_pass = fields.Char(string="Clave Teams"  )    

    street = fields.Char('Calle', related="partner_id.street" , readonly=False )
    street2 = fields.Char('Calle 2', related="partner_id.street2" , readonly=False)
    phone = fields.Char('Teléfono', related="partner_id.phone" , readonly=False, states={'done': [('readonly', False)]})
    mobile = fields.Char('Mobile', related="partner_id.mobile", readonly=False, states={'done': [('readonly', False)]})
    city = fields.Char('Ciudad', related="partner_id.city",  readonly=False)
    zip = fields.Char('Zip', related="partner_id.zip" , readonly=False)
    state_id = fields.Many2one('res.country.state', 'Estado', related="partner_id.state_id" , readonly=False )
    country_id = fields.Many2one('res.country', 'Päis', related="partner_id.country_id" , readonly=False )
    birth_date = fields.Date('Fecha de nacimiento', required=True, states={'done': [('readonly', False)]})


    application_number = fields.Char(
        string="Application Number",
        required=True, copy=False, readonly=True,
        index='trigram',
        default=lambda self: _('Nuevo'))


    duration_state = fields.Selection(
        selection=[
            ('not_started', 'No iniciado'),
            ('in_progress', 'En curso'),
            ('expired', 'Finalizado')
        ],
        required=True,
        string='Estd. Grupo',
        default="not_started",
        compute='_compute_duration_state',
        store=True
    )

    
    @api.depends('batch_id.end_date', 'state')
    def _compute_duration_state(self):
        today = date.today()
        for record in self:
            if record.state == 'done': 
                if record.batch_id and record.batch_id.end_date:  # Check if batch_id exists
                    if today <= record.batch_id.end_date:
                        record.duration_state = 'in_progress'
                    else:
                        record.duration_state = 'expired'
                else:
                    record.duration_state = 'not_started'
            else:
                record.duration_state = 'not_started'

    def _cron_update_duration_state(self):
        records = self.env['op.admission'].search([])
        records._compute_duration_state()
            
            
    
    @api.onchange('student_id', 'is_student')
    def onchange_student(self):
        if self.is_student and self.student_id:
            sd = self.student_id



    
    @api.depends('application_number','batch_id.teams_domain')
    def compute_teams_email(self):
        for self in self:
            teams_email = ' . . . @ . . . '
            if self.application_number and  self.batch_id.teams_domain:
                teams_email = self.application_number+'@'+self.batch_id.teams_domain.replace('@','')            
            self.teams_email = teams_email.lower()



    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'company_id' in vals:
                self = self.with_company(vals['company_id'])
            if vals.get('application_number', _("Nuevo")) == _("Nuevo"):
                
                vals['application_number'] = self.env['ir.sequence'].next_by_code(
                    'op.admission') or _("Nuevo")

        return super().create(vals_list)
    
    def enroll_student(self):
        for record in self:
            if record.register_id.max_count:
                total_admission = self.env['op.admission'].sudo().search_count(
                    [('register_id', '=', record.register_id.id),
                     ('state', '=', 'done')])
                if not total_admission < record.register_id.max_count:
                    msg = 'Max Admission In Admission Register :- (%s)' % (
                        record.register_id.max_count)
                    raise ValidationError(_(msg))
            if not record.student_id:
                vals = record.get_student_vals()
                record.partner_id = vals.get('partner_id')
                record.student_id = student_id = self.env[
                    'op.student'].sudo().create(vals).id

            else:
                student_id = record.student_id.id
                op_student_course = self.env['op.student.course'].sudo().search([('student_id','=',self.student_id.id),('batch_id','=',self.batch_id.id),('course_id','=',self.course_id.id)]) 
                if not op_student_course:
                    record.student_id.sudo().write({
                        'course_detail_ids': [[0, False, {
                            'course_id':
                                record.course_id and record.course_id.id or False,
                            'batch_id':
                                record.batch_id and record.batch_id.id or False,
                            'fees_term_id': record.fees_term_id.id,
                            'fees_start_date': record.fees_start_date,
                            'product_id': record.register_id.product_id.id,
                        }]],
                    })
            if record.fees_term_id.fees_terms in ['fixed_days', 'fixed_date']:
                val = []
                product_id = record.register_id.product_id.id
                for line in record.fees_term_id.line_ids:
                    no_days = line.due_days
                    per_amount = line.value
                    amount = (per_amount * record.fees) / 100
                    dict_val = {
                        'fees_line_id': line.id,
                        'amount': amount,
                        'fees_factor': per_amount,
                        'product_id': product_id,
                        'discount': record.discount or record.fees_term_id.discount,
                        'state': 'draft',
                        'course_id': record.course_id and record.course_id.id or False,
                        'batch_id': record.batch_id and record.batch_id.id or False,
                    }
                    if line.due_date:
                        date = line.due_date
                        dict_val.update({
                            'date': date
                        })
                    elif self.fees_start_date:
                        date = self.fees_start_date + relativedelta(
                            days=no_days)
                        dict_val.update({
                            'date': date,
                        })
                    else:
                        date_now = (datetime.today() + relativedelta(
                            days=no_days)).date()
                        dict_val.update({
                            'date': date_now,
                        })
                    val.append([0, False, dict_val])
                record.student_id.write({
                    'fees_detail_ids': val
                })
            record.write({
                'nbr': 1,
                'state': 'done',
                'admission_date': fields.Date.today(),
                'student_id': student_id,
                'is_student': True,
            })
            reg_id = self.env['op.subject.registration'].sudo().create({
                'student_id': student_id,
                'batch_id': record.batch_id.id,
                'course_id': record.course_id.id,
                'min_unit_load': record.course_id.min_unit_load or 0.0,
                'max_unit_load': record.course_id.max_unit_load or 0.0,
                'state': 'draft',
            })
            #if not record.phone or not record.mobile:
            #    raise UserError(
            #        _('Please fill in the mobile number'))
            reg_id.get_subjects()
