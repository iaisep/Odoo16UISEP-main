import logging
from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


# class OpBatch(models.Model):
#     _name = 'op.batch'
#     _description = "Asignaturas"


class OpBatch(models.Model):
    _inherit = 'op.batch'

    #slide_channel_id = fields.Many2one('slide.channel', string="Asignatura en Elearning")
    #subject_ids = fields.Many2many('op.subject', string='Subject(s)')
    subject_to_batch_ids = fields.One2many('op.subject.to.batch', 'batch_id', string='Asignaturas en lote')

    @api.model
    def create(self, vals):
        record = super(OpBatch, self).create(vals)
        if 'course_id' in vals:
            course = self.env['op.course'].browse(vals['course_id'])
            for subject in course.subject_ids:
                self.env['op.subject.to.batch'].create({
                    'batch_id': record.id,
                    'subject_id': subject.id,
                    'code': subject.code,
                })
        return record

    def write(self, vals):
        if 'course_id' in vals:
            for record in self:
                record.subject_to_batch_ids.unlink()
                course = self.env['op.course'].browse(vals['course_id'])
                for subject in course.subject_ids:
                    self.env['op.subject.to.batch'].create({
                        'batch_id': record.id,
                        'subject_id': subject.id,
                        'code': subject.code,
                    })
        return super(OpBatch, self).write(vals)
        

class OpSubjectToBatch(models.Model):
    _name = 'op.subject.to.batch'
    _description = "Asignaturas en lote"

    subject_id = fields.Many2one('op.subject', string="Asignatura")
    batch_id = fields.Many2one('op.batch', string="Lote")
    code = fields.Char(string="Código")
    date_to=fields.Date(string="Fecha de Fin")
    date_from=fields.Date(string="Fecha de Inicio")


    @api.onchange('date_from')
    def _onchange_date_from_in_range(self):
        if self.date_from:
            if self.date_from < self.batch_id.start_date:
                self.date_from = False
                return {
                    'warning': {
                        'title': "Error",
                        'message': "La fecha de inicio no puede ser anterior a la fecha de inicio del lote"
                    }
                }
        pass

    @api.onchange('date_to')
    def _onchange_date_to_in_range(self):
        if self.date_to:
            if self.date_to > self.batch_id.end_date:
                self.date_to = False
                return {
                    'warning': {
                        'title': "Error",
                        'message': "La fecha de fin no puede ser posterior a la fecha de fin del lote"
                    }
                }
        pass