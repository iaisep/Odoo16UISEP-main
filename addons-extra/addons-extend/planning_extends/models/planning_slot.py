# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class planning_slot_extends(models.Model):
    _inherit = 'planning.slot'


    project_tasks_id = fields.Many2one('project.task')


    