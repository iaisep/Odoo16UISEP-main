from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

class OpSubject(models.Model):
    _inherit = "op.subject"
    _order = 'sequence, id'

    sequence = fields.Integer(string="Sequence", default=10)
    parent_subject_id = fields.Many2one('op.subject', string="Precedencia Obligatoria")
    course_subject_ids = fields.Many2many(related="course_id.subject_ids")


    def can_be_taken(self, user_id):
        self.ensure_one()
        user = self.env['res.users'].sudo().browse(user_id)
        if not user:
            return False
        course_id = self.course_id or False
        if not course_id:
            return False
        admission_id = self.env['op.admission'].sudo().search([('course_id','=',course_id.id),('student_id.user_id','=',user.id),('state','=','done')], limit=1)
        if not admission_id:
            return False
        if  admission_id.modality == 'manual':
            return True
        p_subject = self.parent_subject_id 
        if not p_subject:
            return True
        p_completion_id= self.env['slide.channel.partner'].sudo().search([('partner_id','=',user.partner_id.id),('op_subject_id','=',p_subject.id),('admission_id','=',admission_id.id)], limit=1)
        if p_completion_id and p_completion_id.completed:
            return True
        return False

    @api.constrains('parent_subject_id')
    def _check_parent_subject_id(self):
        if not self._check_recursion('parent_subject_id'):
            raise ValidationError(_('Recursión detectada en %s. La materia no puede depender de sí misma.',(self.display_name)))

