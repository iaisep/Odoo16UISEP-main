# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

import json
from datetime import timedelta

from babel.dates import format_date, format_datetime

from odoo import _, api, fields, models
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.tools.misc import get_lang


class OpAdmissionRegister(models.Model):
    _inherit = "op.admission.register"

    color = fields.Integer("Color Index", default=0)

    kanban_admission_dashboard_graph = fields.Text(
        compute='_compute_kanban_dashboard_graph')
    admission_count = fields.Integer(compute='_compute_admission_count', store=True)

    @api.depends("admission_ids")
    def _compute_admission_count(self):
        for record in self:
            record.admission_count = len(record.admission_ids)

    def action_onboarding_admission_register_layout(self):
        self.env.user.company_id.onboarding_admission_register_layout_state = \
            'done'

    def action_view_applications(self):
        action = self.env.ref('openeducat_admission.'
                              'act_open_op_admission_view').read()[0]
        action['domain'] = [('id', 'in', self.admission_ids.ids)]
        return action

    def _compute_kanban_dashboard_graph(self):
        for record in self:
            record.kanban_admission_dashboard_graph = json.dumps(
                record.get_lms_bar_graph_datas())

    def _get_bar_graph_select_query(self):
        return ('''SELECT COUNT(*) FROM op_admission LEFT JOIN
                    op_admission_register AS op_reg ON
                    op_admission.register_id = op_reg.id
                    WHERE op_admission.register_id = %s''' % (self.id,)
                )

    def get_lms_bar_graph_datas(self):
        data = []
        today = fields.Datetime.now(self)
        data.append({'label': _('Draft'), 'value': 0.0, 'type': 'past'})
        day_of_week = int(format_datetime(today, 'e', locale=get_lang(self.env).code))
        first_day_of_week = today + timedelta(days=-day_of_week + 1)
        for i in range(-1, 2):
            if i == 0:
                label = _('This Week')
            elif i == 1:
                label = _('Done')
            else:
                start_week = first_day_of_week + timedelta(days=i * 7)
                end_week = start_week + timedelta(days=6)
                if start_week.month == end_week.month:
                    label = str(start_week.day) + '-' + str(end_week.day) + ' ' + \
                        format_date(end_week, 'MMM', locale=get_lang(self.env).code)
                else:
                    label = format_date(start_week, 'd MMM',
                                        locale=get_lang(self.env).code) + '-' + \
                        format_date(end_week, 'd MMM', locale=get_lang(self.env).code)
            data.append({'label': label, 'value': 0.0, 'type': 'past'})

        (select_sql_clause) = self._get_bar_graph_select_query()
        self.env.cr.execute(select_sql_clause)
        query = ''
        start_date = (first_day_of_week + timedelta(days=-7))

        for i in range(0, 6):
            if i == 0:
                query += "(" + select_sql_clause + " and op_admission.state='draft')"
            elif i == 5:
                query += " UNION ALL (" + select_sql_clause + " and op_admission." \
                                                              "state='done')"
            elif i == 1:
                next_date = start_date + timedelta(days=7)
                query += " UNION ALL (" + select_sql_clause + " " \
                    "and op_admission.application_date >= '" + start_date.strftime(
                        DF) + "' and op_admission.application_date <= '" +\
                    end_week.strftime(DF) + "')"
                start_date = next_date
            elif i == 2:
                next_date = start_date + timedelta(days=7)
                query += " UNION ALL (" + select_sql_clause + " " \
                    "and op_admission.application_date > '" + end_week.strftime(
                        DF) + "')"
                start_date = next_date
            else:
                start_date = next_date

        self.env.cr.execute(query)
        query_results = self.env.cr.dictfetchall()
        for index in range(0, len(query_results)):
            data[index]['value'] = query_results[index].get('count')
        return [{'values': data, 'title': _('title'), 'key': _('Admissions')}]
