# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import _, fields, models


class OpAdmission(models.Model):
    _inherit = 'op.admission'

    def _composer_format(self, res_model, res_id, template):
        compose_form = self.env.ref(
            'mail.email_compose_message_wizard_form', False)
        ctx = dict(
            default_model=res_model,
            default_res_id=res_id,
            default_use_template=bool(template),
            default_template_id=template and template.id or False,
            default_composition_mode='comment',
            force_email=True
        )
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }

    # def send_email(self):
    #     self.ensure_one()
    #     template = self.env.ref(
    #         'openeducat_admission_enterprise.email_admission_confirm',
    #         raise_if_not_found=False)
    #     return self._composer_format(res_model='op.admission',
    #                                  res_id=self.id,
    #                                  template=template)


class OpCourse(models.Model):
    _inherit = "op.course"

    admission_count = fields.Integer(
        compute="_compute_admission_count_dashboard_data", string='Admission Count')

    def _compute_admission_count_dashboard_data(self):
        for course in self:
            admission_list = self.env['op.admission'].search_count(
                [('course_id', 'in', [course.id]), ('state', '=', 'done')])
            course.admission_count = admission_list
