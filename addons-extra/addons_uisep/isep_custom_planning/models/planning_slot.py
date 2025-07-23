# -*- coding: utf-8 -*-


from odoo import api, fields, models, _


class PlanningShift(models.Model):
    _inherit = 'planning.slot'


    task_id = fields.Many2one(
        'project.task', string="Tarea", store=True, readonly=False,
        copy=False ,domain="[('company_id', '=', company_id), ('project_id', '=', project_id)]")
    
    