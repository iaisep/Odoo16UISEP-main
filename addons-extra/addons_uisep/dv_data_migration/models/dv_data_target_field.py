from odoo import api, fields, models

class dvDataTargetField(models.Model):
    _name = 'dv.data.target.field'
    _description = 'Data Target Field'

    target_id = fields.Many2one('dv.data.target', 'Target', ondelete='cascade')
    
    origin_column = fields.Char(string='Origin Value')

    origin_column_type = fields.Selection([
        ('column', 'Column'),
        ('column_int', 'Column Integer'),
        ('column_float', 'Column Float'),
        ('fixed', 'Fixed Value'),
        ('fixed_ref', 'Fixed Reference Value'),
        ('m2o_external_code', 'Many2One External Code'),
    ], string="Origin Value Type", default='column', help="Type of the origin column's data source.")
    
    field_id = fields.Many2one('ir.model.fields', 'Field', required=True, ondelete='cascade', domain="[('model_id', '=', parent.model_id)]")
    field_mrelated = fields.Char(string="Modelo de", related='field_id.relation', help="Modelo relaciona del campo many2one a recibir")
    field_ttype = fields.Selection(string="Tipo de", related='field_id.ttype', help="Tipo de campo del campo a recibir")
    field_check_result = fields.Char(string="m_code en", compute="check_m_code_field", help='Existe el campo de referencia m_code dentro del modelo relacionado')

    def check_m_code_field(self):
        for rec in self:            
            if not rec.field_mrelated:
                rec.field_check_result = None
                continue
            
            model_name = rec.field_mrelated
           
            field_exists = self.env['ir.model.fields'].search_count([
                ('model_id.model', '=', model_name),
                ('name', '=', 'm_code')
            ])
            
            if field_exists > 0:
                rec.field_check_result = 'Existe campo'
            else:
                rec.field_check_result = 'No existe campo'


class DvDataTargetFieldNoalma(models.Model):
    _name = 'dv.data.target.field.noalma'
    _description = 'data target no stored'


    target_id = fields.Many2one('dv.data.target', 'Target', ondelete='cascade')
    
    origin_column = fields.Char(string='Origin Value')

    origin_column_type = fields.Selection([
        ('column', 'Column'),
        ('column_int', 'Column Integer'),
        ('column_float', 'Column Float'),
        ('column_m2m', 'Many2Many External Code'),
        ('fixed', 'Fixed Value'),        
        ('fixed_ref', 'Fixed Reference Value'),
        ('m2o_external_code', 'Many2One External Code'),
    ], string="Origin Value Type", default='column', help="Type of the origin column's data source.")
    
    field_id = fields.Many2one('ir.model.fields', 'Field', required=True, ondelete='cascade', domain="[('model_id', '=', parent.model_id)]")
    field_mrelated = fields.Char(string="Modelo de", related='field_id.relation', help="Modelo relaciona del campo many2one a recibir")
    field_ttype = fields.Selection(string="Tipo de", related='field_id.ttype', help="Tipo de campo del campo a recibir")
    field_check_result = fields.Char(string="m_code en", compute="check_m_code_field", help='Existe el campo de referencia m_code dentro del modelo relacionado')

    def check_m_code_field(self):
        for rec in self:            
            if not rec.field_mrelated:
                rec.field_check_result = None
                continue
            
            model_name = rec.field_mrelated
           
            field_exists = self.env['ir.model.fields'].search_count([
                ('model_id.model', '=', model_name),
                ('name', '=', 'm_code')
            ])
            
            if field_exists > 0:
                rec.field_check_result = 'Existe campo'
            else:
                rec.field_check_result = 'No existe campo'