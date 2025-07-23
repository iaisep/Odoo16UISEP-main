# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class AppGradebookStudent(models.Model):
    _inherit = "app.gradebook.student"

    avg_score = fields.Float(string="Promedio General", digits=(6,2), compute="compute_avg_score", store=True)

    @api.depends('student_id','gradebook_subject_ids','gradebook_subject_ids.final_subject_note','gradebook_subject_ids.op_subject_id','gradebook_subject_ids.op_subject_id.subject_type')
    def compute_avg_score(self):
        for rec in self:
            subject_ids = rec.gradebook_subject_ids.filtered(lambda r: r.op_subject_id.subject_type == 'compulsory')
            sum_score = 0.0
            for s_index, subject_id in enumerate(subject_ids, 1):
                sum_score += subject_id.final_subject_note
                 
            rec.avg_score = subject_ids and sum_score/s_index or 0.0
          

    
