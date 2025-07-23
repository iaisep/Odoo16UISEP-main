# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class OpCourse(models.Model):
    _inherit = 'op.course'
    
    activate_tesis = fields.Boolean(string='Activar revision Tesis', default=False, help="Activar para permitir subida para revision de tesis")


class TesisAttachmentWizard(models.TransientModel):
    _name = 'tesis.attachment.wizard'
    _description = 'Wizard para actualizar revisión, nota y comentario del adjunto'

    attachment_id = fields.Many2one('ir.attachment', string="Adjunto", required=True)
    review = fields.Boolean(string="Revisión")
    note_point = fields.Float(string="Nota")
    comment = fields.Text(string="Comentario")

    def action_save_attachment(self):
        """Actualiza el adjunto con los nuevos datos del wizard"""
        self.attachment_id.write({
            'review': self.review,
            'note_point': self.note_point,
            'comment': self.comment,
        })
        return {'type': 'ir.actions.act_window_close'}

    @api.constrains('note_point')
    def _check_points_fin_range(self):
        for rec in self:
            if rec.note_point > 0:
                if rec.note_point < 1 or rec.note_point > 10:
                    raise ValidationError("El punteo debe estar entre 1 y 10.")