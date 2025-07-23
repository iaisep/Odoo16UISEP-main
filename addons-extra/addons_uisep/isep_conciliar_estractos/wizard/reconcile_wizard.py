# -*- coding: utf-8 -*-
import logging

import csv
import base64
import io

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ReconcileWizard(models.TransientModel):
    _name = 'reconcile.wizard'
    _description = _('ReconcileWizard')

    csv_file = fields.Binary(string="CSV File", required=True)
    csv_filename = fields.Char(string="CSV Filename")

    def action_reconcile(self):
        AccountMoveLine = self.env['account.move.line']

        # Decodificar el archivo CSV
        file_content = base64.b64decode(self.csv_file)
        file_content = io.StringIO(file_content.decode('utf-8'))
        reader = csv.DictReader(file_content)

        invoice_ids = []
        statement_line_ids = []

        # Verificar las columnas del CSV
        if 'invoice_id' not in reader.fieldnames or 'statement_line_id' not in reader.fieldnames:
            raise UserError(_('El archivo CSV debe contener las columnas "invoice_id" y "statement_line_id".'))

        for row in reader:
            invoice_ids.append(int(row['invoice_id']))
            statement_line_ids.append(int(row['statement_line_id']))

        if len(invoice_ids) != len(statement_line_ids):
            raise UserError("La cantidad de facturas y líneas de extractos bancarios debe ser igual.")

        for invoice_id, statement_line_id in zip(invoice_ids, statement_line_ids):
            # Obtener la factura
            invoice = self.env['account.move'].browse(invoice_id)
            if not invoice or invoice.state != 'posted':
                raise UserError(f"Factura {invoice_id} no encontrada o no está en estado publicado.")

            # Obtener la línea del extracto bancario
            statement_line = self.env['account.bank.statement.line'].browse(statement_line_id)
            if not statement_line:
                raise UserError(f"Línea de extracto bancario {statement_line_id} no encontrada.")

            # Obtener los movimientos contables de la factura y la línea del extracto
            invoice_move_lines = AccountMoveLine.search([('move_id', '=', invoice_id), ('account_id.reconcile', '=', True)])
            statement_move_lines = AccountMoveLine.search([('move_id', '=', statement_line.move_id.id), ('account_id.reconcile', '=', True)])

            for line in statement_move_lines:
                line.write({'account_id': invoice_move_lines[0].account_id.id})

            # Verificar si las cuentas contables son las mismas
            if not invoice_move_lines or not statement_move_lines:
                raise UserError(f"No se encontraron líneas de movimiento contable conciliables para la factura {invoice_id} o el extracto {statement_line_id}.")

            invoice_accounts = invoice_move_lines.mapped('account_id')
            statement_accounts = statement_move_lines.mapped('account_id')

            if set(invoice_accounts.ids) != set(statement_accounts.ids):
                raise UserError(_("Los asientos de la factura {invoice_id} y la línea del extracto {statement_line_id} no son de la misma cuenta: {} != {}").format(
                    ", ".join(invoice_accounts.mapped('code')),
                    ", ".join(statement_accounts.mapped('code'))
                ))



            # Crear una reconciliación
            (invoice_move_lines + statement_move_lines).reconcile()

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }


    def action_unreconcile(self):
        AccountMoveLine = self.env['account.move.line']

        # Decodificar el archivo CSV
        file_content = base64.b64decode(self.csv_file)
        file_content = io.StringIO(file_content.decode('utf-8'))
        reader = csv.DictReader(file_content)

        invoice_ids = []
        statement_line_ids = []

        # Verificar las columnas del CSV
        if 'invoice_id' not in reader.fieldnames or 'statement_line_id' not in reader.fieldnames:
            raise UserError(_('El archivo CSV debe contener las columnas "invoice_id" y "statement_line_id".'))

        for row in reader:
            invoice_ids.append(int(row['invoice_id']))
            statement_line_ids.append(int(row['statement_line_id']))

        if len(invoice_ids) != len(statement_line_ids):
            raise UserError("La cantidad de facturas y líneas de extractos bancarios debe ser igual.")

        for invoice_id, statement_line_id in zip(invoice_ids, statement_line_ids):
            # Obtener los movimientos contables de la factura y la línea del extracto
            invoice_move_lines = AccountMoveLine.search([('move_id', '=', invoice_id), ('account_id.reconcile', '=', True)])
            statement_move_lines = AccountMoveLine.search([('move_id', '=', self.env['account.bank.statement.line'].browse(statement_line_id).move_id.id), ('account_id.reconcile', '=', True)])

            if not invoice_move_lines or not statement_move_lines:
                raise UserError(f"No se encontraron líneas de movimiento contable conciliables para la factura {invoice_id} o el extracto {statement_line_id}.")

            # Deshacer la reconciliación
            (invoice_move_lines + statement_move_lines).remove_move_reconcile()

            # Actualizar el estado del extracto bancario
            statement_line = self.env['account.bank.statement.line'].browse(statement_line_id)
            statement_line.write({'is_reconciled': False})

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
