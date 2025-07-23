# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

import time

from odoo import fields, models


class OpBatch(models.Model):
    _inherit = 'op.batch'

    lectures_count = fields.Integer(
        compute="_compute_session_count_dashboard_data",
        string='Lectures Count')

    def _compute_session_count_dashboard_data(self):
        for batch in self:
            session_list = self.env['op.session'].search_count([
                ('batch_id', 'in', [batch.id]),
                ('start_datetime', '>=', time.strftime('%Y-%m-%d 00:00:00')),
                ('end_datetime', '<=', time.strftime('%Y-%m-%d 23:59:59'))
            ])
            batch.lectures_count = session_list

    def open_generate_timetable(self):
        action = self.env.ref(
            'openeducat_timetable.act_open_generate_time_table_view').read()[0]
        action.update({'context': "{'default_batch_id': " +
                       str(self.id) + ", 'default_course_id': " +
                       str(self.course_id.id) + "}"})
        return action

    def open_generate_timetable_reports(self):
        action = self.env.ref(
            'openeducat_timetable.act_open_time_table_report_view').read()[0]
        action.update({'context':
                       "{'default_state': 'student','default_batch_id': " +
                       str(self.id) + ", 'default_course_id': " +
                       str(self.course_id.id) + "}"})
        return action
