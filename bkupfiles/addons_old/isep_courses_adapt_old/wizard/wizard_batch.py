# -*- coding: utf-8 -*-

from datetime import date, datetime
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

class WizardBatch(models.TransientModel):
    _name = "wizard.batch"

    @api.model
    def default_get(self,vals):
        res=super(WizardBatch,self).default_get(vals)
        courses_new=[]
        batch_id=self.env['op.batch'].browse(self.env.context.get('active_id'))
        subject_ex=batch_id.op_batch_subject_rel_ids.mapped('subject_id.id')
        subject_ids=self.env['op.subject'].search([('course_ids','=',batch_id.course_id.id)])
        for line in subject_ids:
            if line.id not in subject_ex: 
                courses_new.append((0,0,{
                        'subject_id': line.id,
                        'check': True
                    }))
        res.update({'subject_ids':courses_new})
        return res

    def action_add_subjet(self):
        batch_id=self.env['op.batch'].browse(self.env.context.get('active_id'))
        subject_ids=self.subject_ids.filtered(lambda x:x.check==True)
        courses_new=[]
        for line in subject_ids:
            #if line.subject_id.id in  subject_ex:
            courses_new.append((0,0,{
                    'subject_id': line.subject_id.id,
                }))
        batch_id.write({'op_batch_subject_rel_ids':courses_new})
        return True

    subject_ids = fields.One2many('wizard.batch.line','wbatch',string='Asignaturas')

class WizardBatchLine(models.TransientModel):
    _name = "wizard.batch.line"
    
    wbatch=fields.Many2one("wizard.batch",string="Lines")
    check=fields.Boolean(string="Seleccionar")
    subject_id = fields.Many2one('op.subject', string="Asignatura")
    code=fields.Char(related="subject_id.code",string="Codigo")
    moodle_id=fields.Char(related="subject_id.moodle_id",string="Moodle ID")
