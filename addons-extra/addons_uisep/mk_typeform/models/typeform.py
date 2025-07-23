# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _


class MkTyperForm(models.Model):
    _name = 'mk.typeform.form'
    _description = 'Typeform form'

    name = fields.Char(
        string='Name'
    )
    typeform_id = fields.Char(
        string='Typeform Form ID'
    )
    internal_model_id = fields.Many2one(
        comodel_name='ir.model',
        string='Odoo model',
        help="Each form submission will generate a new record of this model"
    )
    fields_relations_ids = fields.One2many(
        comodel_name='mk.typeform.model.relation',
        inverse_name='form_id',
        string='Fields relationship'
    )
    submits_ids = fields.One2many(
        comodel_name='mk.typeform.submit',
        inverse_name='form_id',
        string='Submits'
    )
    
    required_fields = fields.Text(string="Campo requerido" , compute="compute_required_fields" , store=True)


    @api.depends('internal_model_id')
    def compute_required_fields(self):
        required_fields = ''
        if self.internal_model_id:
            for line in self.internal_model_id.sudo().field_id.filtered(lambda x: x.required == True):
                required_fields += ('- %s [%s] -> [%s]\n' % (_(line.field_description),(line.name), (line.ttype) )) 
        self.required_fields = required_fields
    

class TypeformModelRelation(models.Model):
    _name = 'mk.typeform.model.relation'
    _description = 'Typeform fields Relationship'

    type_field = fields.Selection(
        string="Type",
        selection=[
            ('reference_type', 'Reference'),
            ('static_type', 'Static'),
            ('search_type', 'Search')
        ],
        required=True,
        default='reference_type'
    )
    format_value = fields.Selection(
        string="Force Format",
        selection=[
            ('int', 'Integer'),
            ('float', 'Decimal'),
            ('str', 'Text')
        ]
    )
    value_static_field = fields.Text(
        string="Static value"
    )
    reference = fields.Char(
        string="Reference"
    )
    form_id = fields.Many2one(
        comodel_name='mk.typeform.form',
        string='Form'
    )
    relation_model_id = fields.Many2one(
        comodel_name='ir.model',
        string='Form Model',
        related='form_id.internal_model_id'
    )
    field_model_id = fields.Many2one(
        comodel_name='ir.model.fields',
        string='Field Model',
        domain="[('model_id', '=', relation_model_id)]"
    )


class Submit(models.Model):
    _name = 'mk.typeform.submit'
    _description = 'Typeform submits'
    _rec_name = 'title'

    submitted_at = fields.Datetime(
        string='Submit Date'
    )
    landed_at = fields.Datetime(
        string='Start date'
    )
    title = fields.Text(
        string='Title'
    )
    res_internal_model_id = fields.Integer(
        string='Internal Model ID'
    )
    res_internal_model_name = fields.Char(
        string='Internal Model Name'
    )
    form_id = fields.Many2one(
        comodel_name='mk.typeform.form',
        string='Form'
    )
    fields_ids = fields.One2many(
        comodel_name='mk.typeform.answer',
        inverse_name='submit_id',
        string='Answers'
    )

    

    def view_internal_model_button(self):
        if not self.res_internal_model_name or not self.res_internal_model_id:
            raise exceptions.UserError(_("There are no objects created for this shipment"))
        return {
            'name': _("Related object {}".format(self.res_internal_model_name)),
            'res_model': self.res_internal_model_name,
            'res_id': self.res_internal_model_id,
            'type': 'ir.actions.act_window',
            'target': 'inline',
            'view_mode': 'form',
            'context': {}
        }


class Answer(models.Model):
    _name = 'mk.typeform.answer'
    _description = 'Typeform Answer'

    title = fields.Text(
        string='Question'
    )
    answer = fields.Text(
        string='Answer'
    )
    file_id = fields.Many2one(
        comodel_name="ir.attachment",
        string="Archivo"
    )
    submit_id = fields.Many2one(
        comodel_name='mk.typeform.submit',
        string='Submit'
    )
    field_rel_id = fields.Many2one(
        comodel_name="mk.typeform.model.relation",
        string="Fields relationship"
    )
    field_id = fields.Many2one(
        comodel_name='ir.model.fields',
        string='Field Model',
        related="field_rel_id.field_model_id"
    )
    reference = fields.Char(
        string="Reference",
        related="field_rel_id.reference"
    )



class CrmLead(models.Model):
    _inherit = 'crm.lead'

    typeform_form_id = fields.Many2one('mk.typeform.form', store=True, readonly=True)