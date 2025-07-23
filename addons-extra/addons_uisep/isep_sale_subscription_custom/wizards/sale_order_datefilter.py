from odoo import models, fields, api
from datetime import datetime ,timedelta
from odoo.exceptions import ValidationError
import xlsxwriter
from odoo.tools import date_utils
from io import BytesIO
import base64
import io


class SaleOrderDateFilterWizard(models.TransientModel):
    _name = 'sale.order.date.filter.wizard'
    _description = 'Wizard para filtrar Órdenes de Venta por Fecha'

    date_field = fields.Selection([
        ('date_order', 'Fecha de pedido'),
        ('create_date', 'Fecha de creación'),
        ('next_invoice_date', 'Fecha siguiente factura'),
        ('subscription_schedule_due', 'Fecha de vencimiento de plazo'),
    ], string="Campo a filtrar", required=True, default='date_order')

    date_from = fields.Date(string="Fecha inicial", required=True)
    date_to = fields.Date(string="Fecha final", required=True, default=fields.Date.context_today)

    def action_apply_filter(self):
        self.ensure_one()
        today = fields.Date.today()
        fixed_domain = [
            ('is_subscription', '=', True),
            ('stage_id.view_cartera', '=', True),
        ]
        if self.date_field == 'subscription_schedule_due':
            date_domain = [
                ('due_line_ids.date_due', '>=', self.date_from),
                ('due_line_ids.date_due', '<=', self.date_to)               
            ]
        else:
            date_domain = [
                (self.date_field, '>=', self.date_from),
                (self.date_field, '<=', self.date_to),
            ]

        return {
            'type': 'ir.actions.act_window',
            'name': 'Cartera filtrada ' + self.date_from.strftime('%d/%m/%Y') + ' a ' + self.date_to.strftime('%d/%m/%Y') + ' - ' + dict(self._fields['date_field'].selection).get(self.date_field, self.date_field),
            'res_model': 'sale.order',
            'view_mode': 'tree,form',
            'views': [
                (self.env.ref('isep_sale_subscription_custom.isep_sale_subscription_cartera_tree').id, 'tree'),
                (False, 'form'),
            ],
            'domain': fixed_domain + date_domain,
            'context': dict(self.env.context, group_by='currency_id'),
        }

    @api.constrains('date_from', 'date_to')
    def _check_date_range(self):
        for rec in self:
            if rec.date_from and rec.date_to and rec.date_from > rec.date_to:
                raise ValidationError("La fecha inicial no puede ser posterior a la fecha final.")

    def action_print_report(self):
        self.ensure_one()
        return self.env.ref('isep_sale_subscription_custom.report_sale_subscription_due_pdf').report_action(self)

    def get_currency_summary(self):
        self.ensure_one()
        orders = self._get_filtered_orders()
        if not orders:
            return []

        today = fields.Date.today()
        summary = {}

        for order in orders:
      
            has_due_lines = order.subscription_schedule.filtered(
                lambda s: s.date_due and s.date_due < today and s.payment_state == 'not_paid'
            )
            if not has_due_lines:
                continue

            currency = order.currency_id.name
            if currency not in summary:
                summary[currency] = {
                    'currency': currency,
                    'amount_untaxed': 0.0,
                    'amount_total': 0.0,
                    'amount_recurring': 0.0,
                }

            summary[currency]['amount_untaxed'] += order.amount_untaxed
            summary[currency]['amount_total'] += order.amount_total
            summary[currency]['amount_recurring'] += order.amount_recurring_taxinc

        return list(summary.values())


    def get_due_lines_grouped(self):
        self.ensure_one()

        orders = self._get_filtered_orders()
        if not orders:
            return []

        grouped = []

        for order in orders:
      
            if self.date_field == 'subscription_schedule_due':
                due_lines = sorted(
                    order.subscription_schedule.filtered(
                        lambda s: (
                            s.date_due and
                            s.payment_state == 'not_paid' and
                            self.date_from <= s.date_due <= self.date_to
                        )
                    ),
                    key=lambda l: l.date_due
                )
            else:
                today = fields.Date.today()
                due_lines = sorted(
                    order.subscription_schedule.filtered(
                        lambda s: (
                            s.date_due and
                            s.payment_state == 'not_paid' and
                            s.date_due < today
                        )
                    ),
                    key=lambda l: l.date_due
                )

            if not due_lines:
                continue

            lines = []
            total = 0.0

            for line in due_lines:
                lines.append({
                    'order_name': order.name,
                    'term': line.term_label or '',
                    'currency': order.currency_id.name,
                    'state': 'SIN PAGAR',
                    'due_date': line.date_due.strftime('%d/%m/%Y') if line.date_due else '',
                    'amount': line.amount_recurring_taxinc,
                })
                total += line.amount_recurring_taxinc

            grouped.append({
                'partner': order.partner_id.name,
                'user': order.user_id.name,
                'amount_recurent': order.amount_recurring_taxinc,
                'next_date_invoice': order.next_invoice_date.strftime('%d/%m/%Y') if order.next_invoice_date else '',
                'order_date': order.date_order.strftime('%d/%m/%Y') if order.date_order else '',
                'lines': lines,
                'total': total,
            })

        return grouped



    def _get_filtered_orders(self):
        self.ensure_one()

        base_domain = [
            ('is_subscription', '=', True),
            ('stage_id.view_cartera', '=', True),
        ]

        if self.date_field == 'subscription_schedule_due':
         
            domain = base_domain
        else:
            domain = base_domain + [
                (self.date_field, '>=', self.date_from),
                (self.date_field, '<=', self.date_to),
            ]

        return self.env['sale.order'].search(domain)


    def get_total_by_currency(self):
        self.ensure_one()
        totals = {}

        for client in self.get_due_lines_grouped():
            if not client['lines']:
                continue
            currency = client['lines'][0]['currency']
            totals[currency] = totals.get(currency, 0.0) + client['total']
        
        return totals

    def action_export_excel(self):
        self.ensure_one()
        orders = self._get_filtered_orders()

        # Diccionario para resultados
        report_data = {}
        all_dates = set()

        for order in orders:
            partner = order.partner_id.name
            if partner not in report_data:
                report_data[partner] = {
                    'total': 0.0,
                    'pagado': 0.0,
                    'residual': 0.0,
                    'dates': {}
                }

            partner_data = report_data[partner]
            partner_data['total'] += order.amount_total
            partner_data['pagado'] += 0
            partner_data['residual'] += 0

            for line in order.subscription_schedule:
                if line.payment_state != 'not_paid' or not line.date_due:
                    continue
                date_str = line.date_due.strftime('%d/%m/%Y')
                all_dates.add(date_str)
                partner_data['dates'][date_str] = partner_data['dates'].get(date_str, 0.0) + line.amount_recurring_taxinc

        sorted_dates = sorted(all_dates, key=lambda d: datetime.strptime(d, '%d/%m/%Y'))

        # Crear archivo Excel en memoria
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet('Cartera')

        # Formatos
        bold = workbook.add_format({'bold': True})
        money = workbook.add_format({'num_format': '#,##0.00'})

        # Encabezado
        headers = ['cliente', 'total', 'total pagado', 'total a resid'] + sorted_dates
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, bold)

        # Cuerpo
        for row, (partner, data) in enumerate(report_data.items(), start=1):
            worksheet.write(row, 0, partner)
            worksheet.write(row, 1, data['total'], money)
            worksheet.write(row, 2, data['pagado'], money)
            worksheet.write(row, 3, data['residual'], money)

            for col, date in enumerate(sorted_dates, start=4):
                amount = data['dates'].get(date, 0.0)
                if amount:
                    worksheet.write(row, col, amount, money)

        workbook.close()
        output.seek(0)

        # Crea un attachment para descarga
        file_data = base64.b64encode(output.read())
        filename = 'Cartera_Subscriptions.xlsx'

        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': file_data,
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        })

        # Acción para descargar
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }


class SaleOrderDateFilterWizard2(models.TransientModel):
    _name = 'sale.order.date.filter.wizard2'
    _description = 'Wizard para filtrar excel cartera'

    date_field = fields.Selection([
        ('date_due', 'Fecha vencimiento'),
        ('create_date', 'Fecha de creación'),
        ('date_schedule', 'Fecha'),
        ('date_executed', 'Fecha ejecutar'),
    ], string="Campo a filtrar", required=True, default='date_due')

    date_from = fields.Date(string="Fecha inicial", required=True)
    date_to = fields.Date(string="Fecha final", required=True)
    currency_id = fields.Many2one(
        string="Moneda",
        comodel_name="res.currency", domain="[('active', '=', True)]",
    )

    file_data = fields.Binary("Archivo Excel")
    file_name = fields.Char("Nombre archivo")
    
    def default_get(self, fields_list):
        res = super(SaleOrderDateFilterWizard2, self).default_get(fields_list)

        today = fields.Date.context_today(self)
        first_day = date_utils.start_of(today, 'month')
        last_day = date_utils.end_of(today, 'month')

        res['date_from'] = first_day
        res['date_to'] = last_day

        return res

    def action_generate_excel(self):
        if self.date_from > self.date_to:
            raise ValidationError("La fecha inicial no puede ser mayor que la fecha final.")

        date_field = self.date_field or 'date_due'
        domain = [(date_field, '>=', self.date_from), (date_field, '<=', self.date_to)]
        domain += [('payment_state', 'in', ['not_paid', 'partial'])]

        if self.currency_id:
            domain.append(('currency_id', '=', self.currency_id.id))

        schedules = self.env['sale.subscription.schedule'].search(domain, order="partner_id, %s" % date_field)

        # Fechas completas del rango
        all_dates = []
        current_date = self.date_from
        while current_date <= self.date_to:
            all_dates.append(current_date)
            current_date += timedelta(days=1)

        # Agrupar info por partner
        data = {}
        for s in schedules:
            key = s.partner_id.id
            fecha = getattr(s, date_field)
            if not fecha:
                continue

            if key not in data:
                data[key] = {
                    'order_name': s.order_id.name or 'N/A',
                    'partner': s.partner_id.name or 'Sin cliente',
                    'currency': s.currency_id.name or '',
                    'total_cobro': s.order_id.total_recurring or 0.0,
                    'total_pagos': s.order_id.total_paid or 0.0,
                    'token_exist': s.token_exist,
                    'montos': {}
                }

            data[key]['montos'][fecha] = data[key]['montos'].get(fecha, 0.0) + s.total_residual

        # Excel
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet("Cobros")

        # Formatos
        date_format = workbook.add_format({'num_format': 'dd/mm/yyyy'})
        money_format = workbook.add_format({'num_format': '$#,##0.00'})
        bold_format = workbook.add_format({'bold': True})

        total_format = workbook.add_format({
            'bold': True,
            'bg_color': '#DDEBF7',
            'border': 1,
            'num_format': '$#,##0.00'
        })

        total_label_format = workbook.add_format({
            'bold': True,
            'bg_color': '#DDEBF7',
            'border': 1
        })

        # Encabezados
        headers = ["Suscripción", "Cliente", "Moneda", "Total Cobro", "Total Pagos", "Residual", "Token"]
        for col_idx, header in enumerate(headers):
            sheet.write(0, col_idx, header, bold_format)

        col_start_fecha = len(headers)
        for col_idx, fecha in enumerate(all_dates, start=col_start_fecha):
            sheet.write_datetime(0, col_idx, fecha, date_format)

        col_total_por_fila = col_start_fecha + len(all_dates)
        sheet.write(0, col_total_por_fila, "Total por fila", bold_format)

        # Ancho columnas
        sheet.set_column(0, 0, 15)   # Suscripción
        sheet.set_column(1, 1, 30)   # Cliente
        sheet.set_column(2, 2, 10)   # Moneda
        sheet.set_column(3, 5, 15)   # Total cobro, pagos, residual
        sheet.set_column(6, 6, 12)   # Token
        for col_idx in range(col_start_fecha, col_total_por_fila + 1):
            sheet.set_column(col_idx, col_idx, 12)

        # Congelar cabecera
        sheet.freeze_panes(1, 3)

        # Filas de datos
        for row_idx, record in enumerate(data.values(), start=1):
            sheet.write(row_idx, 0, record['order_name'])
            sheet.write(row_idx, 1, record['partner'])
            sheet.write(row_idx, 2, record['currency'])
            sheet.write_number(row_idx, 3, record['total_cobro'], money_format)
            sheet.write_number(row_idx, 4, record['total_pagos'], money_format)
            sheet.write_number(row_idx, 5, record['total_cobro'] - record['total_pagos'], money_format)
            sheet.write(row_idx, 6, record['token_exist'])

            total_row_fecha = 0.0
            for col_idx, fecha in enumerate(all_dates, start=col_start_fecha):
                amount = record['montos'].get(fecha, 0.0)
                if amount:
                    sheet.write_number(row_idx, col_idx, amount, money_format)
                    total_row_fecha += amount

            sheet.write_number(row_idx, col_total_por_fila, total_row_fecha, money_format)

        # Fila TOTAL GENERAL
        total_row_idx = len(data) + 2

        # Pintar TODA la fila con fondo celeste (excepto donde se escriben números)
        for col in range(col_total_por_fila + 1):
            if col == 0:
                sheet.write(total_row_idx, col, "TOTAL GENERAL", total_label_format)
            elif col in [3, 4, 5]:  # Se escribirán luego con total_format
                continue
            elif col >= col_start_fecha:
                continue  # Se escribirán luego con total_format
            else:
                sheet.write(total_row_idx, col, "", total_label_format)

        # Totales monetarios fijos
        sheet.write_number(total_row_idx, 3, sum(r['total_cobro'] for r in data.values()), total_format)
        sheet.write_number(total_row_idx, 4, sum(r['total_pagos'] for r in data.values()), total_format)
        sheet.write_number(total_row_idx, 5, sum((r['total_cobro'] - r['total_pagos']) for r in data.values()), total_format)
        sheet.write(total_row_idx, 6, "", total_label_format)

        # Totales por fecha
        total_general_por_fecha = 0.0
        for col_idx, fecha in enumerate(all_dates, start=col_start_fecha):
            total_fecha = sum(r['montos'].get(fecha, 0.0) for r in data.values())
            total_general_por_fecha += total_fecha
            sheet.write_number(total_row_idx, col_idx, total_fecha, total_format)

        # Total por fila (suma de fechas)
        sheet.write_number(total_row_idx, col_total_por_fila, total_general_por_fecha, total_format)

        # Guardar
        workbook.close()
        output.seek(0)

        filecontent = base64.b64encode(output.read())
        filename = f"Cobros_{self.date_from.strftime('%Y%m%d')}_{self.date_to.strftime('%Y%m%d')}.xlsx"

        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': filecontent,
            'res_model': 'sale.order.date.filter.wizard2',
            'res_id': self.id,
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        })

        download_url = f'/web/content/{attachment.id}?download=true'

        return {
            "type": "ir.actions.act_url",
            "url": download_url,
            "target": "self",
        }
