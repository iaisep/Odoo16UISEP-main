import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date

_logger = logging.getLogger(__name__)



class OpElearningSubjectWizard(models.TransientModel):
    _name = "op.elearning.subject.wizard"
    _description = "Elearning subject Wizard"
    _order = "code, name asc"
    

    admission_wizard_id = fields.Many2one('op.admission.elearning.wizard')
    name = fields.Char(string="ASIGNATURA")
    code = fields.Char(string="COD.")
    course_id = fields.Many2one('op.course', string="CURSO" )
    op_subject_id = fields.Many2one('op.subject', string="ASIGNATURA" )
    slide_channel_id = fields.Many2one('slide.channel', string="EN CAMPUS")
    selected = fields.Boolean(string="INSCRIBIR")
    channel_partner_id = fields.Many2one('slide.channel.partner', string="Alumno incrito, existente")
    alter_subject = fields.Boolean(string="Asignatura no curricular")


    @api.model
    def create(self, vals):
        res = super(OpElearningSubjectWizard, self).create(vals)
        channel_partner_id = res.default_selected()
        if channel_partner_id:
            res.channel_partner_id = channel_partner_id
            if res.channel_partner_id.active == True:
                res.selected = True
            else:
                res.selected = False
        return res

    def default_selected(self):
        channel_id = self.env['slide.channel.partner'].search([
                    ('active','=',True),
                    ('channel_id','=', self.slide_channel_id.id),
                    ('partner_id','=', self.admission_wizard_id.partner_id.id)] , limit=1)
        if not channel_id:
            channel_id = self.env['slide.channel.partner'].search([
                    ('active','=',False),
                    ('channel_id','=', self.slide_channel_id.id),
                    ('partner_id','=', self.admission_wizard_id.partner_id.id)] , limit=1)
        
        return channel_id
    

class OpAdmissionElearningWizard(models.TransientModel):
    _name = "op.admission.elearning.wizard"
    _description = "Inscripcion en Campus Universitario"

    partner_id = fields.Many2one('res.partner', string="Alumno" )
    subject_line_ids = fields.One2many('op.elearning.subject.wizard', 'admission_wizard_id', string='Asignaturas')
    
    course_id = fields.Many2one('op.course', string="Curso" )     
    batch_id = fields.Many2one('op.batch', string="Grupo" )
    register_id = fields.Many2one('op.admission.register', string="Registro de Admisión" )
    admission_id = fields.Many2one('op.admission', string="Admission" )

    def enroll_student(self):
        for line in self.subject_line_ids:
            #raise UserError(str(line.selected))
            if line.channel_partner_id:
                line.channel_partner_id.active=line.selected
                line.channel_partner_id.course_id=self.course_id.id
                line.channel_partner_id.batch_id=self.batch_id.id
                line.channel_partner_id.register_id=self.register_id.id
                line.channel_partner_id.admission_id=self.admission_id.id        

            elif not line.channel_partner_id and line.selected:
                self.env['slide.channel.partner'].create({
                        'active': True,
                        'channel_id': line.slide_channel_id.id,
                        'partner_id':self.partner_id.id,
                        'course_id': self.course_id.id,
                        'batch_id': self.batch_id.id,
                        'op_subject_id': line.op_subject_id.id,                        
                        'register_id': self.register_id.id,
                        'admission_id': self.admission_id.id,})  
            


class OpAdmissionRegister(models.Model):
    _inherit = 'op.admission.register'

    
    def send_mail_all(self):
        for line in self.admission_ids:
            line.send_mail(True)



class OpAdmission(models.Model):
    _inherit = 'op.admission'

    # tutor_id = fields.Many2one('res.partner', string="Tutor" )
    email_send_ok = fields.Boolean('Correo de bienvenida enviado')
    consul_down_id = fields.Many2one('admission.downconsult', string='Consultas de retiro')

    state = fields.Selection(
        selection_add=[('down', 'Retirado')]
    )
    mail_down = fields.Boolean('Correo de retiro enviado', store=True,default=False)

    def action_down(self):
        down_consult = self.env['admission.downconsult'].sudo().create({
            'admission_id': self.id, 
        })
        self.consul_down_id = down_consult.id
        self.state = 'down'
        if self.order_id:
            self._cancel_unpaid_invoices_by_order(self.order_id.id)
        self.message_post(
            body=_(f"Se inició la encuesta de retiro. Encuesta vinculada a: <a href='#' data-oe-model='admission.downconsult' data-oe-id='{down_consult.id}'>{down_consult.name}</a>"),
            subject="Inicio de Encuesta de Retiro"
        )
        return True

    def _cancel_unpaid_invoices_by_order(self, order_id):
        SaleOrder = self.env['sale.order'].sudo()
        AccountMove = self.env['account.move'].sudo()
        sale_order = SaleOrder.search([('id', '=', order_id)], limit=1)
        if not sale_order:
            return
        unpaid_invoices = AccountMove.search([
            ('order_subscription_id', '=', sale_order.id),
            ('state', '=', 'posted'),
            ('payment_state', '=', 'not_paid')
        ])

        for invoice in unpaid_invoices:
            if invoice.state == 'posted':
                invoice.button_draft()
            invoice.button_cancel()

    # def action_send_down_mail(self):   
    #     for rec in self:
    #         ctx = {}
    #         email_list = rec.email
    #         base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
    #         survey = self.env.ref('isep_elearning_custom.survey_baja_estudiante')
    #         if email_list:
    #             ctx['email_to'] = email_list
    #             ctx['email_from'] = self.env.user.partner_id.email
    #             ctx['send_email'] = True
    #             ctx['attendee'] = rec.partner_id.name
    #             template = self.env.ref('isep_elearning_custom.email_template_down_report')
    #             template.with_context(ctx).send_mail(self.id, force_send=True, raise_exception=False)
    #             rec.update({
    #                 'mail_down' : True,
    #             }) 
    #         else:
    #             rec.update({
    #                 'mail_down' : False,
    #             })

    # def action_print_report_donw(self):
    #     return self.env.ref('isep_elearning_custom.action_report_down_adminsion').report_action(self)


    def get_student_vals(self):
        for student in self:
            vals = {
                'name': student.name,
                'login': student.email,
                'image_1920': self.image or False,
                'is_student': True,
                'company_id': self.company_id.id,
                'groups_id': [
                    (6, 0,
                     [self.env.ref('base.group_portal').id])]
            }
            if self.partner_id:
                vals['partner_id'] =  self.partner_id.id
                

            student_user = self.env['res.users'].sudo().create(vals)

            details = {
                'title': student.title and student.title.id or False,
                'first_name': student.first_name,
                'middle_name': student.middle_name,
                'last_name': student.last_name,
                'birth_date': student.birth_date,
                'gender': student.gender,
                'image_1920': student.image or False,
                'course_detail_ids': [[0, False, {
                    'course_id':
                        student.course_id and student.course_id.id or False,
                    'batch_id':
                        student.batch_id and student.batch_id.id or False,
                    'academic_years_id':
                        student.register_id.academic_years_id.id or False,
                    'academic_term_id':
                        student.register_id.academic_term_id.id or False,
                    'fees_term_id': student.fees_term_id.id,
                    'fees_start_date': student.fees_start_date,
                    'product_id': student.register_id.product_id.id,
                }]],
                'user_id': student_user.id,
                'company_id': self.company_id.id,
                'partner_id': student_user.partner_id.id,
            }
            student_user.with_context(create_user=1).sudo().action_reset_password()
            # student_user.action_reset_password()
            return details


    def submit_form(self):
        email = False
        if self.email:
            email = self.email.lower().strip()
            self.email = email
        result_search = self.env['res.users'].sudo().search([('email','=', email)], limit=1)
        partner_id = False
        # raise UserError(str(result_search))
        if result_search and self.email:
            partner_id = result_search.partner_id
            user_id = result_search.id
            student_id = self.env['op.student'].sudo().search([('user_id','=', user_id)], limit=1)
            if not student_id:
                # student_user.partner_id.write(details)
                details = {
                    'title': self.title and self.title.id or False,
                    'first_name': self.first_name,
                    'middle_name': self.middle_name,
                    'last_name': self.last_name,
                    'birth_date': self.birth_date,
                    'gender': self.gender,
                    'image_1920': self.image or False,
                    'user_id': result_search.id,
                    'company_id': self.company_id.id,
                    'partner_id': partner_id.id,
                }
                student_id = self.env['op.student'].create(details)

            self.is_student = True
            self.partner_id = partner_id.id
            self.student_id = student_id.id
            


        if not result_search:
            if self.sale_line_id.order_partner_id:
                partner_id = self.sale_line_id.order_partner_id.id
            if not self.sale_line_id.order_partner_id:
                result_partner_id = self.env['res.partner'].sudo().search([('email','=', email)], limit=1)
                if result_partner_id:
                    partner_id = result_partner_id.id
            if not partner_id:
                partner_id = self.env['res.partner'].sudo().search([('email','=', email)], limit=1)
                if  not partner_id:
                    values_partner = {
                        'name': self.name,
                        'email': self.email,
                        'street':self.street,
                        'street2':self.street2,
                        'city':self.city,
                        'zip': self.zip,
                        'country_id':self.country_id.id,
                        'state_id':self.state_id.id,
                        'phone':self.phone,
                        'mobile':self.mobile,
                        'title': self.title.id
                    }
                    partner_id = partner_id.sudo().create(values_partner)

            self.partner_id = partner_id
        self.state = 'submit'

    def send_mail_view(self):
        self.send_mail(True)

    def send_mail(self, force):
        if not self.email_send_ok:
            student_name = self.name # '[%s] %s %s %s' % (self.application_number or '',self.first_name or '',self.middle_name or '',self.last_name or '')
            if not self.tutor_id:
                raise UserError('%s - El aplicante necesita un Tutor asignado.' % (student_name))
            if not self.batch_id.start_date:
                raise UserError('%s - Necesita establecer fecha de inicio de Clases.' % (student_name))
            if not self.batch_id:
                raise UserError('%s - Necesita asignar un grupo.' % (student_name))            
            template_id = self.env.ref('isep_elearning_custom.email_op_admission_confirm').id
            self.with_context(force_send=force).message_post_with_template(template_id, email_layout_xmlid=False)
            self.email_send_ok = True
        # self.with_context(force_send=True).message_post_with_template(template_id, email_layout_xmlid='mail.mail_notification_light')


    def enroll_elearning_wizard(self):
        if not self.course_id:
            raise UserError('El curso es requerido.')
        if not self.student_id.user_id:
            raise UserError('El Alumno necesita un usuario.')
        
        if not self.register_id:
            raise UserError('El registro de admisión es requerido.')
        
        if not self.batch_id:
            raise UserError('El Grupo es requerido.')      


        user_student = self.student_id.user_id.partner_id
        values = {
            'admission_id': self.id,
            'course_id': self.course_id.id,
            'partner_id': user_student.id,
            'batch_id': self.batch_id.id,
            'register_id': self.register_id.id
        }
        wizard = self.env['op.admission.elearning.wizard'].create(values)

        for line in self.course_id.subject_ids:
            wizard_line = {
                'name': line.name ,
                'course_id':self.course_id.id,
                'op_subject_id': line.id,
                'code': line.code or '',
                'slide_channel_id': line.slide_channel_id.id,                
                'admission_wizard_id': wizard.id,
            }
            self.env['op.elearning.subject.wizard'].create(wizard_line)
        for line in self.course_id.slide_channel_ids:
            wizard_line = {
                'name': 'ASIGNATURA COMPLEMENTARIA' ,
                'course_id':self.course_id.id,
                'op_subject_id': False,
                'code': '----' or '',
                'slide_channel_id': line.id,                
                'admission_wizard_id': wizard.id,
                'alter_subject': True,
            }
            self.env['op.elearning.subject.wizard'].create(wizard_line)

        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("isep_elearning_custom.campus_content_elearning")        
        action['res_id'] = wizard.id
        return action


    def auto_enroll_student(self):
        """ Automatiza la inscripción de los alumnos y desactiva registros si ha pasado la fecha de finalización. """
        today = date.today()        
        for record in self:
            if record.state == 'done':
                if not record.batch_id:
                    continue
                
                for subject_batch in record.batch_id.subject_to_batch_ids:
                    if not subject_batch.subject_id.slide_channel_id:
                        continue  
                    if not subject_batch.date_from or not subject_batch.date_to:
                        continue 
                    channel_partners = self.env['slide.channel.partner'].search([
                        ('partner_id', '=', record.partner_id.id),
                        ('channel_id', '=', subject_batch.subject_id.slide_channel_id.id),
                        ('batch_id', '=', record.batch_id.id),
                    ])
                    #print("aaqui///////////////////////////////",channel_partners)

                    if subject_batch.date_from <= today <= subject_batch.date_to:
                        if channel_partners:
                            channel_partners.write({
                                'active': True,
                                'course_id': record.course_id.id,
                                'register_id': record.register_id.id,
                                'admission_id': record.id,
                                'date_from': subject_batch.date_from,
                                'date_to': subject_batch.date_to,
                            })
                        else:
                            self.env['slide.channel.partner'].create({
                                'active': True,
                                'channel_id': subject_batch.subject_id.slide_channel_id.id,
                                'partner_id': record.partner_id.id,
                                'course_id': record.course_id.id,
                                'batch_id': record.batch_id.id,
                                'date_from': subject_batch.date_from,
                                'date_to': subject_batch.date_to,
                                'op_subject_id': subject_batch.subject_id.id,
                                'register_id': record.register_id.id,
                                'admission_id': record.id,
                            })

                    elif today > subject_batch.date_to and channel_partners:
                        channel_partners.write({'active': False})

    def cron_auto_enroll_student(self):

        today = date.today()

        admissions = self.search([('state', '=', 'done'), ('batch_id', '!=', False)])

        for record in admissions:
            for subject_batch in record.batch_id.subject_to_batch_ids:
                if not subject_batch.subject_id.slide_channel_id:
                    continue

                if not subject_batch.date_from or not subject_batch.date_to:
                    continue 

                channel_partner = self.env['slide.channel.partner'].sudo().search([
                    ('partner_id', '=', record.partner_id.id),
                    #('op_subject_id', '=', subject_batch.subject_id.id),
                    ('channel_id', '=', subject_batch.subject_id.slide_channel_id.id),
                    '|',  # Operador OR para incluir registros activos y desactivados
                    ('active', '=', True),
                    ('active', '=', False),
                ], order='create_date ASC', limit=1)
                #print("aaqui///////////////////////////////",channel_partner)

                if subject_batch.date_from <= today <= subject_batch.date_to:
                    
                    if channel_partner:                       
                        channel_partner.write({
                            'active': True,
                            'course_id': record.course_id.id,
                            'register_id': record.register_id.id,
                            'admission_id': record.id,
                            'batch_id': record.batch_id.id,
                            'date_from': subject_batch.date_from,
                            'date_to': subject_batch.date_to,
                        })

                    else:    
                       # print("CREANDO///////////////////////////////********")                  
                        self.env['slide.channel.partner'].create({
                            'active': True,
                            'channel_id': subject_batch.subject_id.slide_channel_id.id,
                            'partner_id': record.partner_id.id,
                            'course_id': record.course_id.id,
                            'batch_id': record.batch_id.id,
                            'date_from': subject_batch.date_from,
                            'date_to': subject_batch.date_to,
                            'op_subject_id': subject_batch.subject_id.id,
                            'register_id': record.register_id.id,
                            'admission_id': record.id,
                        })

                elif today > subject_batch.date_to and channel_partner:
                    channel_partner.write({'active': False})