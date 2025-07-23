# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import api, fields, models


class AcademicCalendar(models.Model):
    _inherit = "calendar.event"

    academic_calendar = fields.Boolean(string="Academic Calendar?")
    course_ids = fields.Many2many("op.course", string="Courses")
    batch_ids = fields.Many2many("op.batch", string="Batches",
                                 domain="[('course_id', 'in',course_ids)]")

    @api.onchange('course_ids')
    def onchange_all_course(self):
        for rec in self:
            if rec.course_ids:
                rec.academic_calendar = True
            else:
                rec.academic_calendar = False


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    global_calendar_user_id = fields.Many2one(
        string='Calendar User',
        comodel_name='res.users',
        config_parameter='global_calendar_user_id'
    )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(global_calendar_user_id=int(
            self.env['ir.config_parameter'].sudo(
            ).get_param('global_calendar_user_id')),
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()
        param.set_param('global_calendar_user_id', int(self.global_calendar_user_id.id))
