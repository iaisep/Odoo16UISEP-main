from odoo import models, fields, api
import json



class AppGradebookPending(models.TransientModel):
    _name = 'app.gradebook.pending'
    _description = "AppGradebookPending"


    name = fields.Char('Nombre', default="Asignaciones/Exámenes por Calificar")
    search = fields.Char('Buscar')
    survey_user_input_ids = fields.Many2many('survey.user_input', string='Asignaciones por Calificar',   copy=False )
    user_id = fields.Many2one('res.users', string='Usuario', default=lambda self: self.env.user.id )    

    op_subject_ids = fields.Many2many('op.subject', string='Asignaturas',  copy=False )

    batch_ids = fields.Many2many('op.batch', string='Grupos',  copy=False )
    
    
    def search_gradebook_pending(self):
        domain = [('result_id','=',False),('admission_id','!=',False), ('survey_type','in', ('exam','assignment')  )]
        if self.search:
            domain += [('partner_id.name','ilike',self.search)]
        if self.user_id:
            channel_ids = self.env['slide.channel.partner'].sudo().search([('partner_id','=',self.user_id.partner_id.id)]).mapped('channel_id').ids
            domain += [('channel_id','in',channel_ids)]
        if self.op_subject_ids:
            domain  += [('op_subject_id','in',self.op_subject_ids.mapped('id') )]
        if self.batch_ids:
            domain  += [('batch_id','in',self.batch_ids.mapped('id') )]

        self.survey_user_input_ids = self.env['survey.user_input'].sudo().search(domain)
        # return True