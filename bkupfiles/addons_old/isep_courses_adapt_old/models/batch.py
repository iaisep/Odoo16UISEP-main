# -*- coding: utf-8 -*-

from datetime import date, datetime
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

class OpBatch(models.Model):
    _inherit = "op.batch"

    def action_wizard_subjet(self):
        self.ensure_one()
        module=__name__.split('addons.')[1].split('.')[0]
        view=self.env.ref('%s.view_wizard_batch_from'%module)
        return {
            'name':'Agregar Asignaturas',
            'view_type':'form',
            'view_mode':'form',
            'res_model':'wizard.batch',
            'view_id':view.id,
            'target':'new',
            'type':'ir.actions.act_window'
        }


    modality_id = fields.Many2one('op.modality', string='Modalidad')
    op_batch_subject_rel_ids = fields.One2many('op.batch.subject.rel',
                                               'batch_id')

    _sql_constraints = [
        ('unique_batch_code',
         'unique(name, code)', 'El codigo y nombre del Grupo debe ser unico')
        ]

class OpBatchSubjectRel(models.Model):
    _name = 'op.batch.subject.rel'
    _description = "Subject relations"
    _order = "subject_id desc"

    @api.depends('hours')
    def _compute_creditd(self):
        for this in self:
            this.credits=this.hours*.0625


    sequence = fields.Integer(string='Secuencia')
    batch_id = fields.Many2one('op.batch', string="Batch")
    subject_id = fields.Many2one('op.subject', string="Asignatura")
    code=fields.Char(related="subject_id.code",string="Codigo")
    moodle_id=fields.Char(related="subject_id.moodle_id",string="Moodle ID")
    hours = fields.Float(string="Horas")
    credits = fields.Float(compute='_compute_creditd',string="Creditos",digits=(6,3))

    
    ects = fields.Float(string="ECTS", default=0)
    nif_faculty = fields.Char(string="Teacher's NIF", size=20)
    evaluable = fields.Boolean(string='Is evaluable', default=True)
    level = fields.Char(string="Level", size=1)
    optional = fields.Boolean(string='Is optional', default=False)
    