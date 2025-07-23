# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import fields, models


class OpStudentCourse(models.Model):
    _inherit = "op.student.course"

    session_count = fields.Integer(compute='_compute_count_session')

    def get_session(self):
        action = self.env.ref('openeducat_timetable.'
                              'act_open_op_session_view').read()[0]
        action['domain'] = [('course_id', '=', self.course_id.id),
                            ('batch_id', '=', self.batch_id.id)]
        return action

    def _compute_count_session(self):
        for record in self:
            if record.course_id.id and record.batch_id.id:
                session = self.env['op.session'].search_count(
                    [('course_id', '=', self.course_id.id),
                     ('batch_id', '=', self.batch_id.id)])
                record.session_count += session
