# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

import json
from datetime import datetime

from odoo import fields, models


class OpBatch(models.Model):
    _inherit = "op.batch"

    def _compute_total_present(self):
        for batch in self:
            present = self.env['op.attendance.sheet'].search([
                ('batch_id', '=', batch.id),
                ('attendance_date', '=', datetime.today())])
            if present:
                for pres in present:
                    batch.total_present_student = pres.total_present or 0
            else:
                batch.total_present_student = 0

    def _compute_total_absent(self):
        for batch in self:
            absent = self.env['op.attendance.sheet'].search([
                ('batch_id', '=', batch.id),
                ('attendance_date', '=', datetime.today())])
            if absent:
                for absnt in absent:
                    batch.total_absent_student = absnt.total_absent or 0
            else:
                batch.total_absent_student = 0

    def _compute_kanban_dashboard_graph(self):
        for record in self:
            record.kanban_dashboard_graph = json.dumps(
                record.get_bar_graph_datas())

    kanban_dashboard_graph = fields.Text(
        compute='_compute_kanban_dashboard_graph')
    total_present_student = fields.Integer(
        'Total Present', compute='_compute_total_present')
    total_absent_student = fields.Integer(
        'Total Absent', compute='_compute_total_absent')

    def create_attendance_sheet(self):
        action = self.env.ref(
            'openeducat_attendance.act_open_op_attendance_sheet_view') \
            .read()[0]
        action.update({'views': [[False, 'form']]})
        return action

    def get_bar_graph_datas(self):
        data = []
        attendance = self.env['op.attendance.sheet']
        for day in range(1, fields.date.today().day + 1):
            value = attendance.search([
                ('batch_id', '=', self.id),
                ('attendance_date', '=', fields.date.today().replace(
                    day=day))],
                limit=1)
            data.append({'label': str(day),
                         'value': value and value.total_present or 0})
        return [{'values': data}]
