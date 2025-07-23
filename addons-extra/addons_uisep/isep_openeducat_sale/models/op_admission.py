import logging
from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class OpAdmission(models.Model):
    _inherit = 'op.admission'

    sale_id = fields.Many2one('sale.order', string="Pedido de Venta" , copy=False)  
    sale_line_id = fields.Many2one('sale.order.line', string="Line de Pedido" , copy=False)
    email = fields.Char('Email', size=256, required=True, states={'done': [('readonly', True)]},
                        related='partner_id.email')
    
    @api.model
    def create(self, vals):
        res=super(OpAdmission, self).create(vals)
        res.search_user_portal()
        if res.sale_line_id:
            res.sale_line_id.admission_id = res.id
        return res
    
    def search_user_portal(self):
        if self.sale_id:
            if not self.partner_id or not self.student_id or not self.is_student:
                user_ids = self.sale_id.partner_id.user_ids
                user_id = False
                student_id = False
                for user in user_ids:
                    if user.partner_id ==  self.sale_id.partner_id:
                        user_id = user
                        break
                # User_line es el estudiante en un many2many
                if user_id:
                    if user_id.user_line:
                        for student in user_id.user_line:
                            if student.partner_id ==  self.sale_id.partner_id:
                                student_id = student
                                break
                if user_id and student_id:
                    self.is_student = True
                    self.partner_id = self.sale_id.partner_id.id
                    self.student_id = student_id.id
                    self.phone = self.sale_id.partner_id.phone
                    self.mobile = self.sale_id.partner_id.mobile
                    self.email = self.sale_id.partner_id.email


    def submit_form(self):
        res=super(OpAdmission, self).submit_form()
        self.search_user_portal()        
        return res

        