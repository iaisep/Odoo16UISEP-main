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

    assignment_count = fields.Integer(compute='_compute_count_assignment',
                                      readonly=True)

    def get_assignment(self):
        action = self.env.ref(
            'openeducat_assignment.'
            'act_open_op_assignment_view').read()[0]
        action['domain'] = [('faculty_id', '=', self.id)]
        return action

    def _compute_count_assignment(self):
        for record in self:
            assignments = self.env['op.assignment']. \
                search_count([('faculty_id', '=', record.id)])
            record.assignment_count += assignments

    def action_get_assignment(self):
        assignment_ids = self.env['op.assignment']. \
            search_count([('faculty_id', 'in', self.ids)])
        action = self.env.ref('openeducat_assignment.'
                              'act_open_op_assignment_view').read()[0]
        if (assignment_ids) >= 1:
            action['domain'] = [('faculty_id', 'in', self.ids)]
        else:
            form_view = [
                (self.env.ref('openeducat_assignment.'
                              'view_op_assignment_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [
                    (state, view) for
                    state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = assignment_ids
        context = {}
        if len(self) == 1:
            context.update({
                'default_faculty_id': self.id,
            })
        action['context'] = context
        return action
