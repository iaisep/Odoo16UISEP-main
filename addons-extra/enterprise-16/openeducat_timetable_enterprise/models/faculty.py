# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################

from odoo import fields, models


class OpFaculty(models.Model):
    _inherit = "op.faculty"

    timetable_count = fields.Integer(compute='_compute_count_timetable')

    def get_timetable(self):
        action = self.env.ref(
            'openeducat_timetable.'
            'act_open_op_session_view').read()[0]
        action['domain'] = [('faculty_id', '=', self.id)]
        return action

    def _compute_count_timetable(self):
        for record in self:
            session = self.env['op.session']. \
                search_count([('faculty_id', '=', record.id)])
            record.timetable_count += session

    def action_get_session(self):
        time_ids = self.env['op.session']. \
            search_count([('faculty_id', 'in', self.ids)])
        action = self.env.ref('openeducat_timetable.'
                              'act_open_op_session_view').read()[0]
        if (time_ids) >= 1:
            action['domain'] = [('faculty_id', 'in', self.ids)]
        else:
            form_view = [
                (self.env.ref('openeducat_timetable.'
                              'view_op_session_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [
                    (state, view) for
                    state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = time_ids
        context = {}
        if len(self) == 1:
            context.update({
                'default_faculty_id': self.id,
            })
        action['context'] = context
        return action
