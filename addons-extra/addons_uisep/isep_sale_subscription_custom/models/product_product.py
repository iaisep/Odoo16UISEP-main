from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError




class ProductProduct(models.Model):
    _inherit = 'product.product'

    subscription_plan = fields.Many2one('product.term.schedule', string='Plan de Suscripción' )

"""

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    subscription_plan = fields.Many2one('product.term.schedule', string='Plan de Suscripción', compute='_compute_subscription_plan',
        inverse='_set_subscription_plan', store=True )

    def _set_subscription_plan(self):
        for template in self:
            if len(template.product_variant_ids) == 1:
                template.product_variant_ids.subscription_plan = template.subscription_plan
    
    
    @api.depends('product_variant_ids', 'product_variant_ids.subscription_plan')
    def _compute_subscription_plan(self):
        unique_variants = self.filtered(lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            template.subscription_plan = template.product_variant_ids.subscription_plan
        for template in (self - unique_variants):
            template.subscription_plan = False"""

    
