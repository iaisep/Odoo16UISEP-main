# -*- coding: utf-8 -*-
from odoo import models, fields

class AccountMove(models.Model):
    _inherit = 'account.move'

    event_id = fields.Many2one('calendar.event', help="Para vincular la factura con el evento del calendario.")

class AppointmentPrice(models.Model):
    """
    Este modelo hereda de `appointment.type` para agregar algunos
    campos personalizados.
    """
    _inherit = 'appointment.type'

    has_payment_step = fields.Boolean("Pago por adelantado",
                                      help="Requerir que los visitantes paguen para confirmar su reserva")
    product_id = fields.Many2one(
        'product.product', string="Producto",
        help="Producto configurado para la reserva de citas",
        domain=[('detailed_type', '=', 'tarifas_cita_en_linea')],
        readonly=False, store=True)

class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    invoice_ids = fields.One2many('account.move', 'event_id',
                                  help="Para vincular la factura con el evento del calendario.")

class ProductTemplate(models.Model):
    """
    Se agrega un nuevo tipo de producto para la reserva de citas.
    """
    _inherit = "product.template"

    detailed_type = fields.Selection(selection_add=[
        ('tarifas_cita_en_linea', 'Tarifas de Reserva'),
    ], help="Se agregó un nuevo tipo detallado para la reserva de citas",
        ondelete={'tarifas_cita_en_linea': 'set service'})

    def _detailed_type_mapping(self):
        """
        Se agrega un nuevo tipo de producto para la reserva de citas.
        """
        type_mapping = super()._detailed_type_mapping()
        type_mapping['tarifas_cita_en_linea'] = 'service'
        return type_mapping
