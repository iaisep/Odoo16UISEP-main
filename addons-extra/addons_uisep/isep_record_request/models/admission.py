from odoo import fields, models


class OpAdmission(models.Model):
    _inherit = 'op.admission'

    birth_date = fields.Date('Fecha de nacimiento', required=True, states={'done': [('readonly', False)]},
                             related='partner_id.birth_date')

    # def enroll_student(self):
    #     super(OpAdmission, self).enroll_student()
    #     self.env['record.request'].create({'op_admission_id': self.id})
