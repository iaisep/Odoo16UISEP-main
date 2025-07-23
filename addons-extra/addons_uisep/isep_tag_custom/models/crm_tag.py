# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class CrmTag(models.Model):
    _inherit = "crm.tag"

    code = fields.Integer(string="Id Mautic", required=False, help="Id Mautic")
    partner_tags_id = fields.Many2one(
        'res.partner.tags', 
        string="Categoría Contacto Vinculada", 
        ondelete="set null"
    )

    @api.constrains('code')
    def _check_unique_code(self):
        for rec in self:
            if rec.code and self.search_count([('code', '=', rec.code), ('id', '!=', rec.id)]) > 0:
                raise ValidationError("El código id Mautic debe ser único para cada tag CRM.")

    @api.model
    def create(self, vals):
        tag = super().create(vals)

        if self.env.context.get('create_from_tags'):
            return tag

        partner_tags = self.env['res.partner.tags'].with_context(create_from_tag=True).create({
            'name': tag.name,
            'code': tag.code,
            'color': tag.color,
            'crm_tag_id': tag.id,
        })
        tag.partner_tags_id = partner_tags.id

        return tag

    def write(self, vals):
        res = super().write(vals)
        for tag in self:
            if self.env.context.get('syncing_from_tags'):
                continue  

            tags = tag.partner_tags_id
            if tags:
                update_vals = {}
                if 'name' in vals:
                    update_vals['name'] = tag.name
                if 'code' in vals:
                    update_vals['code'] = tag.code
                if 'color' in vals:
                    update_vals['color'] = tag.color
                if update_vals:
                    tags.with_context(syncing_from_tag=True).write(update_vals)
        return res

    def unlink(self):
        for tag in self:
            if tag.partner_tags_id:
                tag.partner_tags_id.with_context(unlink_from_tag=True).unlink()
        return super().unlink()


    
            
class ResPartnertags(models.Model):
    _inherit = "res.partner.tags"

    code = fields.Integer(string="Id Mautic", required=False, help="Id Mautic")
    crm_tag_id = fields.Many2one(
        'crm.tag',
        string="Etiqueta CRM Vinculada",
        ondelete="set null"
    )

    @api.constrains('code')
    def _check_unique_code(self):
        for rec in self:
            if rec.code and self.search_count([('code', '=', rec.code), ('id', '!=', rec.id)]) > 0:
                raise ValidationError("El código id Mautic debe ser único para cada tag de Contactos.")

    @api.model
    def create(self, vals):
        tags = super().create(vals)

        if self.env.context.get('create_from_tag'):
            return tags

        tag = self.env['crm.tag'].with_context(create_from_tags=True).create({
            'name': tags.name,
            'code': tags.code,
            'color': tags.color,
            'partner_tags_id': tags.id,
        })
        tags.crm_tag_id = tag.id

        return tags


    def write(self, vals):
        res = super().write(vals)
        for tags in self:
            if self.env.context.get('syncing_from_tag'):
                continue  

            tag = tags.crm_tag_id
            if tag:
                update_vals = {}
                if 'name' in vals:
                    update_vals['name'] = tags.name
                if 'code' in vals:
                    update_vals['code'] = tags.code
                if 'color' in vals:
                    update_vals['color'] = tags.color
                if update_vals:
                    tag.with_context(syncing_from_tags=True).write(update_vals)
        return res


    def unlink(self):
        for tags in self:
            if self.env.context.get('unlink_from_tag'):
                continue  
            if tags.crm_tag_id:
                tags.crm_tag_id.with_context(unlink_from_tags=True).unlink()
        return super().unlink()

    
