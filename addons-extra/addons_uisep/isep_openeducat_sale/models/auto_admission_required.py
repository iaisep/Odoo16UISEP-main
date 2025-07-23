from odoo import models, fields, api
from odoo.exceptions import ValidationError

class AutoAdmissionRequired(models.Model):
    _name = 'auto.admission.required'
    _description = 'Auto Admission Required'

    name = fields.Char(string='Nombre', required=True)
    
    mx_active = fields.Boolean(string="Activar auto matricula")
    mx_auto_email_welcome = fields.Boolean(string="Enviar correo de bienvenida")
    mx_state_admission_done = fields.Boolean(string="Admisión en estado HECHO")
    mx_tutor_id = fields.Many2one('res.users', string="Tutor de Orientación" )
    mx_professor_id = fields.Many2one('res.users', string="Tutor de Académico" )
    mx_coordinator = fields.Many2one('res.partner', string="Coordinador" )
    mx_teams_domain = fields.Char(string="Dominio de teams" )
    mx_teams_link = fields.Char(string="Enlace de inducción" )
    mx_teams_msg = fields.Html(string="Mensaje para teams" )
    mx_modality_id = fields.Many2one('op.modality', string="Modalidad" )
    
    br_active = fields.Boolean(string="Activar auto matricula")
    br_auto_email_welcome = fields.Boolean(string="Enviar correo de bienvenida")
    br_state_admission_done = fields.Boolean(string="Admisión en estado HECHO")
    br_tutor_id = fields.Many2one('res.users', string="Tutor de Orientación" )
    br_professor_id = fields.Many2one('res.users', string="Tutor de Académico" )
    br_coordinator = fields.Many2one('res.partner', string="Coordinador" )
    br_teams_domain = fields.Char(string="Dominio de teams" )
    br_teams_link = fields.Char(string="Enlace de inducción" )
    br_teams_msg = fields.Html(string="Mensaje para teams" )
    br_modality_id = fields.Many2one('op.modality', string="Modalidad" )
    
    @api.model
    def create(self, vals):
        if self.search_count([]) >= 1:
            raise ValidationError("Solo puede existir un registro.")
        return super().create(vals)

    def write(self, vals):
        if len(self) > 1:
            raise ValidationError("No puedes modificar multiples registros.")
        return super().write(vals)