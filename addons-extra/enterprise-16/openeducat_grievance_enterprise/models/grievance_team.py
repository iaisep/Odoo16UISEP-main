# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################


from odoo import fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    grievance_team_id = fields.Many2one(
        'grievance.team', "Grievance Team", )


class GrievanceTeam(models.Model):
    _name = "grievance.team"
    _inherit = ['mail.thread']
    _description = "Grievance Team"

    def _compute_grievance_count(self):
        for team in self:
            team.grievance_count = self.env['grievance'].search_count([
                ('grievance_team_id', '=', team.id)])

    grievance_count = fields.Integer(compute='_compute_grievance_count',
                                     string='Total Grievances')
    name = fields.Char("Name", required=True)
    team_leader = fields.Many2one("res.users", "Team Leader", required=True)
    member_ids = fields.One2many("res.users", 'grievance_team_id', string="Members")
    grievance_category_id = fields.Many2many('grievance.category',
                                             string="Grievance Category",
                                             domain=[('parent_id', '!=', False)])
    color = fields.Integer('Color Index', default=1)
