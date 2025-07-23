import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date

_logger = logging.getLogger(__name__)



class OpElearningSubjectWizard(models.TransientModel):
    _inherit = "op.elearning.subject.wizard"
    
    can_be_taken = fields.Boolean(compute="_compute_can_be_taken")


    def _compute_can_be_taken(self):
        for rec in self:
            rec.can_be_taken = False
            user_id = rec.admission_wizard_id.admission_id.student_id.user_id.id or False
            if user_id:
                rec.can_be_taken = rec.op_subject_id.can_be_taken(user_id)


    @api.model
    def create(self, vals):
        res = super(OpElearningSubjectWizard, self).create(vals)
        channel_partner_id = res.default_selected()
        if channel_partner_id:
            res.channel_partner_id = channel_partner_id
            if res.channel_partner_id.active == True:
                res.selected = res.admission_wizard_id.admission_id.modality == 'manual' or res.can_be_taken 
            else:
                res.selected = False
        return res

