from odoo import fields, models, api


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    checklist_ids = fields.One2many(comodel_name='crm.checklist', string='Check list', inverse_name='lead_id', store=True)

    progress = fields.Float("Progreso", store=True, group_operator="avg" )

    @api.onchange('checklist_ids')
    def onchange_checklist(self):
        for self in self:
            # dejo la funcion publica por si hace falta refresh en los registros
            # line_ids = self.env['crm.checklist.line'].search([('evaluar','=',True),('type','=','lead')])
            list_ids = []
            for line in self.checklist_ids:
                list_ids.append(line.checklist_id.id)
            
            list_ids = set(list_ids)
            
            qty = 0

            div_aux = self.env['crm.checklist.line'].search([('evaluar','=',True),('type','=','lead') ])
            div_aux = sum(div_aux.filtered(lambda x: self.team_id.id in x.team_ids.ids ).mapped('qty'))
            
            for x in list_ids:
                x_qty = self.env['crm.checklist.line'].browse(x).qty
                
                len_qty = len(self.checklist_ids.filtered(lambda z: z.checklist_id.id == x))
                if x_qty >= len_qty:
                    qty += len_qty 
                else:
                    qty += x_qty


            if div_aux > 0:
                self.progress = round((qty / div_aux) * 100)
            else:
                self.progress = 0

