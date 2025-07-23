from odoo import models, fields, api
from odoo.exceptions import UserError,ValidationError
from dateutil.relativedelta import relativedelta
from datetime import datetime



class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'

    jh_monthly_fee_check = fields.Boolean(
        string='Usar mensualidad personalizada',
        help='Marca si este contacto tiene una mensualidad fija para cálculo de comisión'
    )
    jh_currency_id = fields.Many2one('res.currency', string="Moneda", default=lambda self: self.env.company.currency_id.id)
    jh_monthly_fee = fields.Float(string="Valor Mensualidad", help="Valor base mensual para comisión")
    jh_fee_percent = fields.Float(string="Porcentaje de la Mensualidad", help="Porcentaje de la mensualidad para calculo de comisión")
    jh_commission_apply_once = fields.Boolean(
        string='Aplicar comisión una sola vez por visita',
        help='Si está activo, la comisión se calcula una sola vez por venta, sin multiplicarse por cantidad de productos.'
    )

    @api.model
    def create(self, vals):
        if not vals.get('jh_currency_id'):
            vals['jh_currency_id'] = self.env.company.currency_id.id
        return super().create(vals)

    def write(self, vals):
        if not vals.get('jh_currency_id'):
            for record in self:
                if not record.jh_currency_id:
                    vals['jh_currency_id'] = self.env.company.currency_id.id
        return super().write(vals)


class ProductTemplateInherit (models.Model):
    _inherit = 'product.template'

    jh_fee_product_chek = fields.Boolean(string='Usar comisión fija')
    jh_fixed_fee_percent = fields.Float(string="Porcentaje de Comisión",
                                          help="Porcentaje para calculo de comisión")
    jh_monthly_fee_product_check = fields.Boolean(
        string='Usar mensualidad por producto',
        help='Marca si este producto tiene una mensualidad fija para cálculo de comisión'
    )
    jh_monthly_fee_product = fields.Float(string="Valor Mensualidad", help="Valor base mensual para comisión")
    jh_monthly_duration = fields.Integer(string='Duración Mensualidad', help='Duración en meses de la mensualidad')
    jh_monthly_commission =fields.Integer(string='Maximo de Meses con Comisión', help='Cantidad de meses de la comisión')
    jh_product_fee_percent = fields.Float(string="Porcentaje de la Mensualidad",
                                          help="Porcentaje de la mensualidad para calculo de comisión")
    jh_currency_id = fields.Many2one('res.currency', string="Moneda",
                                     default=lambda self: self.env.company.currency_id.id)

    @api.constrains('jh_fee_product_chek', 'jh_monthly_fee_product_check')
    def _check_exclusive_commission_mode(self):
        for product in self:
            if product.jh_fee_product_chek and product.jh_monthly_fee_product_check:
                raise ValidationError(
                    "No puedes activar simultáneamente 'Usar comisión fija' y 'Usar mensualidad por producto'. "
                    "Selecciona solo uno de los modos de comisión."
                )

    @api.model
    def create(self, vals):
        if not vals.get('jh_currency_id'):
            vals['jh_currency_id'] = self.env.company.currency_id.id
        return super().create(vals)

    def write(self, vals):
        if not vals.get('jh_currency_id'):
            for record in self:
                if not record.jh_currency_id:
                    vals['jh_currency_id'] = self.env.company.currency_id.id
        return super().write(vals)

class AffiliateCommissionSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    jh_monthly_fee_global_check = fields.Boolean(
        string='Usar mensualidad Global',
        help='Marca si quieres una mensualidad fija para cálculo de todas las comisiónes',
        config_parameter='jh_customizations_affiliate.jh_monthly_fee_global_check'
    )

    jh_global_monthly_fee_percent = fields.Float(
        string='Porcentaje global sobre la mensualidad',
        help='Porcentaje que se aplicará como comisión si no hay configuración específica en el producto o el contacto',
        config_parameter='jh_customizations_affiliate.jh_global_monthly_fee_percent'
    )

    jh_monthly_global_fee = fields.Float(
        string="Valor Mensualidad",
        help="Valor base mensual para comisión",
        config_parameter='jh_customizations_affiliate.jh_monthly_global_fee'
    )

    jh_global_commission_apply_once = fields.Boolean(
        string='Aplicar comisión una sola vez por visita',
        help='Si está activo, la comisión se calcula una sola vez por venta, sin multiplicarse por cantidad de productos.',
        config_parameter='jh_customizations_affiliate.jh_global_commission_apply_once'
    )

    jh_currency_id = fields.Many2one(
        'res.currency',
        string="Moneda",
        default=lambda self: self.env.company.currency_id.id,
        config_parameter='jh_customizations_affiliate.jh_currency_id'
    )

class AffiliateVisitInherit(models.Model):
    _inherit = 'affiliate.visit'

    jh_type_compute = fields.Char(
        string='Método de Cálculo',
        store=True
    )

    jh_quantity_commission = fields.Integer(
        string='Actual de Comisiones',
        compute='_compute_jh_quantity_commission',
        store=False
    )

    def get_commission_cycle_base(self, producto, cliente_vat, afiliado_id, duracion_meses):
        assert self._name == 'affiliate.visit' and len(self) == 1, "Este método debe llamarse sobre una visita única"

        hoy = self.create_date.replace(tzinfo=None)
        visitas_grupo = self.env['affiliate.visit'].search([
            ('sales_order_line_id.product_id', '=', producto.id),
            ('sales_order_line_id.order_id.partner_id.vat', '=', cliente_vat),
            ('affiliate_partner_id', '=', afiliado_id),
            ('state', '=', 'confirm')
        ], order='create_date asc')

        for v in visitas_grupo:
            inicio = v.create_date.replace(tzinfo=None)
            fin = inicio + relativedelta(months=duracion_meses)
            if inicio <= hoy <= fin:
                return inicio, fin

        # Si no hay ciclo vigente, usar fecha actual como base
        return hoy, hoy + relativedelta(months=duracion_meses)

    @api.depends('jh_type_compute')
    def _compute_jh_quantity_commission(self):
        for visit in self:
            producto = visit.sales_order_line_id.product_id
            cliente_vat = visit.sales_order_line_id.order_id.partner_id.vat
            afiliado_id = visit.affiliate_partner_id.id
            duracion_meses = producto.product_tmpl_id.jh_monthly_duration or 0

            if not producto or not cliente_vat or not afiliado_id or duracion_meses <= 0:
                visit.jh_quantity_commission = 0
                continue

            inicio_ciclo, fin_ciclo = visit.get_commission_cycle_base(producto, cliente_vat, afiliado_id,
                                                                      duracion_meses)

            visitas_ciclo = visit.env['affiliate.visit'].search([
                ('sales_order_line_id.product_id', '=', producto.id),
                ('sales_order_line_id.order_id.partner_id.vat', '=', cliente_vat),
                ('affiliate_partner_id', '=', afiliado_id),
                ('state', '=', 'confirm'),
                ('create_date', '>=', inicio_ciclo),
                ('create_date', '<=', fin_ciclo),
                ('id', '!=', visit.id)
            ])

            visit.jh_quantity_commission = sum(v.product_quantity or 0 for v in visitas_ciclo)

    def advance_pps_type_calc(self):
        product = self.sales_order_line_id.product_id.product_tmpl_id
        partner = self.affiliate_partner_id
        config = self.env['ir.config_parameter'].sudo()

        # Nivel 1: Comisión fija sin tope, por cantidad vendida
        if product.jh_fee_product_chek:
            percent = product.jh_fixed_fee_percent or 0.0
            precio_unitario = self.sales_order_line_id.price_unit or 0.0
            qty = self.product_quantity or 1

            commission_total = precio_unitario * percent * qty
            porcentaje_str = f"{int(percent * 100)}%"

            self.amt_type = f"{porcentaje_str} - Comisión fija sin límite - Producto"
            self.jh_type_compute = "1. Comisión por Producto"
            self.commission_amt = commission_total
            return percent * 100, commission_total, 'product'

        # Nivel 1: Comisión mensual con tope por ciclo
        if product.jh_monthly_fee_product_check:
            percent = product.jh_product_fee_percent or 0.0
            fee = product.jh_monthly_fee_product or 0.0
            max_commission_months = product.jh_monthly_commission or 0
            qty = self.product_quantity or 1
            acumuladas = self.jh_quantity_commission or 0

            # 📊 Cálculo de unidades aplicables dentro del tope
            unidades_disponibles = max_commission_months - acumuladas
            unidades_aplicables = min(unidades_disponibles, qty)

            if unidades_aplicables <= 0:
                self.amt_type = (
                    f"Sin comisión - El afiliado '{self.affiliate_partner_id.name}' ya alcanzó el "
                    f"número máximo de comisiones ({max_commission_months}) por suscripción del producto "
                    f"'{product.name}' para el cliente '{self.sales_order_line_id.order_id.partner_id.name}'"
                )
                self.jh_type_compute = "1. Comisión por Producto"
                self.commission_amt = 0.0
                return percent * 100, 0.0, 'product'

            # ✅ Cálculo proporcional según unidades bonificadas
            commission_unitaria = fee * percent
            commission_total = commission_unitaria * unidades_aplicables
            porcentaje_str = f"{int(percent * 100)}%"

            if unidades_aplicables < qty:
                self.amt_type = (
                    f"{porcentaje_str} - Comisión limitada a {unidades_aplicables}/{qty} unidades - Producto"
                )
            else:
                self.amt_type = f"{porcentaje_str} - Comisión otorgada - Producto"

            self.jh_type_compute = "1. Comisión por Producto"
            self.commission_amt = commission_total
            return percent * 100, commission_total, 'product'

        # Nivel 2: Contacto
        if partner.jh_monthly_fee_check:
            percent = partner.jh_fee_percent or 0.0
            fee = partner.jh_monthly_fee or 0.0
            qty = self.product_quantity or 1
            apply_once = partner.jh_commission_apply_once

            base_commission = fee * percent
            commission = base_commission / qty if apply_once else base_commission

            tipo_aplicacion = "Único" if apply_once else "Total"
            porcentaje_str = f"{int(percent * 100)}%"  # Ej. 0.3 → "30%"

            # Diligenciamos los campos de trazabilidad directamente
            self.amt_type = f"{porcentaje_str} - {tipo_aplicacion} - Afiliado"
            self.jh_type_compute = "2. Comisión por Afiliado"

            return percent * 100, commission, 'partner'

        # Nivel 3: Configuración global
        if config.get_param('jh_customizations_affiliate.jh_monthly_fee_global_check'):
            percent = float(config.get_param('jh_customizations_affiliate.jh_global_monthly_fee_percent', default=0))
            fee = float(config.get_param('jh_customizations_affiliate.jh_monthly_global_fee', default=0))
            qty = self.product_quantity or 1
            apply_once = config.get_param('jh_customizations_affiliate.jh_global_commission_apply_once') == 'True'

            if apply_once:
                commission = fee * percent / qty
                tipo_aplicacion = "Único"
            else:
                commission = fee * percent
                tipo_aplicacion = "Total"

            porcentaje_str = f"{int(percent * 100)}%"  # Ej. 0.3 → "30%"
            self.amt_type = f"{porcentaje_str} - {tipo_aplicacion} - Global"
            self.jh_type_compute = "3. Comisión Global"

            return percent * 100, commission, 'global'

        # Nivel Legacy: Ningún cálculo aplicable
        return 0.0, 0.0, 'default'

    def _get_rate(self, affiliate_method, affiliate_type, type_id):
        product = self.sales_order_line_id.product_id
        client = self.sales_order_line_id.order_id.partner_id
        qty = self.product_quantity or 1

        # 🧩 Ruta 1: Comisión fija sin límite
        if product.jh_fee_product_chek:
            percent = product.jh_fixed_fee_percent or 0.0
            precio_unitario = self.sales_order_line_id.price_unit or 0.0

            commission_total = precio_unitario * percent * qty
            porcentaje_str = f"{int(percent * 100)}%"

            self.amt_type = f"{porcentaje_str} - Comisión fija por unidad - Producto"
            self.jh_type_compute = "1. Comisión por Producto"
            self.commission_amt = commission_total

            return {
                'is_error': 0,
                'percentage': percent * 100,
                'amount': commission_total,
                'type': 'product'
            }

        # 📆 Ruta 2: Comisión mensual con duración y tope
        elif product.jh_monthly_fee_product_check:
            percent = product.jh_product_fee_percent or 0.0
            fee = product.jh_monthly_fee_product or 0.0
            max_commission_months = product.jh_monthly_commission or 0
            acumuladas = self.jh_quantity_commission or 0

            # 🔒 Validación de configuración mínima
            if percent == 0.0 or fee == 0.0 or max_commission_months == 0:
                return {
                    'is_error': 1,
                    'message': (
                        f"Comisión no configurada: el producto '{product.name}' requiere valores definidos en "
                        f"'Usar mensualidad por producto', porcentaje, monto mensual y duración."
                    )
                }

            unidades_disponibles = max_commission_months - acumuladas
            unidades_aplicables = min(unidades_disponibles, qty)

            if unidades_aplicables <= 0:
                self.amt_type = (
                    f"Sin comisión - El afiliado '{self.affiliate_partner_id.name}' ya alcanzó el "
                    f"número máximo de comisiones ({max_commission_months}) por suscripción del producto "
                    f"'{product.name}' para el cliente '{client.name}'"
                )
                self.jh_type_compute = "1. Comisión por Producto"
                self.commission_amt = 0.0
                return {
                    'is_error': 0,
                    'percentage': percent * 100,
                    'amount': 0.0,
                    'type': 'product'
                }

            # ✅ Cálculo proporcional por unidades bonificadas
            commission_unitaria = fee * percent
            commission_total = commission_unitaria * unidades_aplicables
            porcentaje_str = f"{int(percent * 100)}%"

            if unidades_aplicables < qty:
                self.amt_type = (
                    f"{porcentaje_str} - Comisión limitada a {unidades_aplicables}/{qty} unidades - Producto"
                )
            else:
                self.amt_type = f"{porcentaje_str} - Comisión otorgada - Producto"

            self.jh_type_compute = "1. Comisión por Producto"
            self.commission_amt = commission_total

            return {
                'is_error': 0,
                'percentage': percent * 100,
                'amount': commission_total,
                'type': 'product'
            }

        # 🚫 Sin lógica de comisión activa
        return {
            'is_error': 1,
            'message': (
                f"Comisión no configurada: el producto '{product.name}' no tiene activado ningún modo de comisión. "
                f"Selecciona 'Usar comisión fija' o 'Usar mensualidad por producto'."
            )
        }
