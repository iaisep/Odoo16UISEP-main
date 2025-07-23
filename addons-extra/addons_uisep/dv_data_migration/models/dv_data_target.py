from odoo import api, fields, models, exceptions, _
import ast
import json
import logging
import xmlrpc.client
from odoo.http import request
from random import randint
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)


class dvDataTarget(models.Model):
    _name = 'dv.data.target'
    _description = 'Data Target'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order= "sequence desc"

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char('Name', required=True)
    data_source_id = fields.Many2one('dv.data.source', string='Data Source')    
    query = fields.Text(string="Query")
    allow_parcial_transaction = fields.Boolean(string="Allow Parcial Transaction")
    origin_primary_key = fields.Char(string="Origin Primary Key")
    target_external_id = fields.Many2one('ir.model.fields', 'Target External Id', required=True,  ondelete='cascade', domain="[('model_id', '=', model_id)]")
    model_id = fields.Many2one('ir.model', 'Target Model', required=True, ondelete='cascade')
    field_ids = fields.One2many('dv.data.target.field', 'target_id', 'Fields')
    field_noalma_ids = fields.One2many('dv.data.target.field.noalma', 'target_id', 'Fields')
    sequence = fields.Integer('Secuencia', default=1)
    tdone=fields.Boolean("Funciono")
    result = fields.Text(string='Query Result')  
    active_c_xmlrpc = fields.Boolean(string="Activa creacion", help="Por defecto busca registros ya creados e inserta cambios, al activar permite crear registros")
    color = fields.Integer(string='Color', default=_get_default_color,
        help="Identifique por color la transaccion")
    note=fields.Text(string="Notas")
    method=fields.Selection([('1','Metodo normal'),
                             ('2','Metodo masivo')], string="Metodo sync", default="1", help="Si el mentodo normal tarda mucho intentengo con metodo masivo")
    model_dv_id = fields.Many2one('dv.model.lines', 'Target Model', required=False, help="Si la tabla destino ha cambiado a la de origen indicar que tabla se copiara")
    
    def massive_ejecution(self):
        if self.tdone:
            _logger.info(f"////* INICIANDO EL REGISTRO DE .... {self.name} */////")
            try:
                if self.field_ids:
                    self.method_sync_button()
                if self.field_noalma_ids:
                    self.migrar_datos()
            except Exception as e:
                raise UserError(f"Error en el registro '{self.name}': {str(e)}")

    def button_ejecution(self):
        _logger.info(f"////* INICIANDO EL REGISTRO DE .... {self.name} */////")
        try:
            if self.field_ids:
                self.method_sync_button()
            if self.field_noalma_ids:
                self.migrar_datos()
        except Exception as e:
            raise UserError(f"Error en el registro '{self.name}': {str(e)}")

    def migrar_datos(self):
        url = self.data_source_id.url_rpc
        db = self.data_source_id.db_rpc
        username = self.data_source_id.username_rpc
        password = self.data_source_id.password_rpc
        model_name = self.model_dv_id.name if self.model_dv_id else self.model_id.model

        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, username, password, {})

        if not uid:
            raise Exception("Error de autenticación en Odoo 15")

        models_old = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

        fields_to_read = []
        for field in self.field_noalma_ids:
            if field.origin_column_type in ['column', 'column_int', 'column_float']:
                if field.origin_column not in fields_to_read:
                    fields_to_read.append(field.origin_column)
            elif field.origin_column_type in ['m2o_external_code', 'column_m2m']:
                # field.origin_column es 'origin_field_name,target_field_name'
                origin_field_name = field.origin_column.split(',')[0].strip()
                if origin_field_name not in fields_to_read:
                    fields_to_read.append(origin_field_name)
            elif field.origin_column_type in ['fixed', 'fixed_ref', 'formula']:
                pass 

        if self.origin_primary_key and self.origin_primary_key not in fields_to_read:
            fields_to_read.append(self.origin_primary_key)

        record_ids = models_old.execute_kw(db, uid, password, model_name, 'search', [[]])


        records = models_old.execute_kw(
            db, uid, password, model_name, 'read', [record_ids], {'fields': fields_to_read}
        )

        for record in records:
            vals = {}
            vals[self.target_external_id.name] = record[self.origin_primary_key]

            for field in self.field_noalma_ids:
                try:
                    field_value = record.get(field.origin_column)
                    if field.origin_column_type == 'column':
                        if field.field_ttype in ['date', 'datetime']:
                            vals[field.field_id.name] = field_value or None
                        elif field.field_ttype == 'many2one':
                            if field_value:
                                if isinstance(field_value, list):
                                    vals[field.field_id.name] = field_value[0]  # Usamos el ID
                                else:
                                    vals[field.field_id.name] = int(field_value)
                            else:
                                vals[field.field_id.name] = False
                        else:
                            vals[field.field_id.name] = field_value or ''
                    elif field.origin_column_type == 'column_int':
                        if isinstance(field_value, list):
                            vals[field.field_id.name] = int(field_value[0])
                        else:
                            vals[field.field_id.name] = int(field_value or 0)
                    elif field.origin_column_type == 'column_float':
                        if isinstance(field_value, list):
                            vals[field.field_id.name] = float(field_value[0])
                        else:
                            vals[field.field_id.name] = float(field_value or 0.0)
                    elif field.origin_column_type == 'fixed':
                        vals[field.field_id.name] = field.origin_column
                    elif field.origin_column_type == 'fixed_ref':
                        vals[field.field_id.name] = int(field.origin_column)
                    elif field.origin_column_type == 'formula':
                        pass 
                    elif field.origin_column_type == 'm2o_external_code':
                        origin_field_name, target_field_name = [s.strip() for s in field.origin_column.split(',')]
                        external_code = record.get(origin_field_name)
                        if external_code:
                            if isinstance(external_code, list):
                                external_code_value = external_code[0]
                            else:
                                external_code_value = external_code
                            related_model = self.env[field.field_id.relation]
                            existing_rel = related_model.search([(target_field_name, '=', external_code_value)], limit=1)
                            if existing_rel:
                                vals[field.field_id.name] = existing_rel.id
                            else:
                                vals[field.field_id.name] = False

                    elif field.origin_column_type == 'column_m2m':
                        origin_field_name, target_field_name = [s.strip() for s in field.origin_column.split(',')]
                        old_ids = record.get(origin_field_name)
                        if old_ids:
                            if not isinstance(old_ids, list):
                                old_ids = [old_ids]
                            related_model = self.env[field.field_id.relation]
                            existing_rel = related_model.search([(target_field_name, 'in', old_ids)])
                            listdv=existing_rel.ids
                            vals[field.field_id.name] = [(6, 0, listdv)]
                        else:
                            print(f"No hay IDs para el campo '{origin_field_name}' en este registro.")
                            _logger.info(f"No hay IDs para el campo '{origin_field_name}' en este registro.")


                    
                except Exception as field_error:
                    _logger.error(f"Error al procesar el campo {field.field_id.name}: {str(field_error)}")
                    self.message_post(body=f"Error al procesar el campo {field.field_id.name} para el registro {record}: {str(field_error)}")
                    if not self.allow_parcial_transaction:
                        raise exceptions.UserError(f"Error al procesar el campo {field.field_id.name} para el registro {record}: {str(field_error)}")

            existing_record = self.env[self.model_id.model].search([(self.target_external_id.name, '=', record[self.origin_primary_key])], limit=1)

            try:
                with self.env.cr.savepoint():
                    if existing_record:
                        existing_record.write(vals)
                        _logger.info(f"Registro actualizado: {existing_record}")
                    else:
                        if self.active_c_xmlrpc == True:
                            new_record = self.env[self.model_id.model].create(vals)
                            _logger.info(f"Nuevo registro creado: {new_record}")
            except Exception as e:
                _logger.error(f"Error al guardar el registro {record}: {str(e)}")
                self.message_post(body=f"Error al guardar el registro {record}: {str(e)}")
                if not self.allow_parcial_transaction:
                    raise exceptions.UserError(f"Error al guardar el registro {record}: {str(e)}")

        self.message_post(body="Successful data migration NO STORED")

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': 'Your data migration was successful! NO STORED',
                'sticky': False,
                'type': 'success',
            },
        }

    def method_sync_button(self):
        if self.method == '1':
            self.button_sync_data1()
        elif self.method == '2':
            self.button_sync_data2()

    def button_sync_data1(self):
        self.ensure_one()

        headers, rows = self.data_source_id.execute_query(self.query)

        for row_data in rows:
            row = dict(zip(headers, row_data))
            vals = {}
            vals[self.target_external_id.name] = row[self.origin_primary_key]

            for field in self.field_ids:
                try:
                    if field.origin_column_type == 'column':
                        if field.field_ttype == 'date' or field.field_ttype == 'datetime':
                            vals[field.field_id.name] = row[field.origin_column] if row[field.origin_column] else None
                        else:
                            vals[field.field_id.name] = row[field.origin_column] if row[field.origin_column] not in [None, ''] else ''
                    elif field.origin_column_type == 'column_int':
                        vals[field.field_id.name] = int(row[field.origin_column]) if row[field.origin_column] not in [None, ''] else 0
                    elif field.origin_column_type == 'column_float':
                        vals[field.field_id.name] = float(row[field.origin_column]) if row[field.origin_column] not in [None, ''] else 0
                    elif field.origin_column_type == 'column_m2m':
                         ids_list = ast.literal_eval(field.origin_column)
                         vals[field.field_id.name] = [(6, 0, ids_list)] # esta opcion necesita quemar los ids que se necesitan agregar ejem [1,2,3] funcion anterior en nostored no funciona en storeds
                    elif field.origin_column_type == 'fixed':
                        vals[field.field_id.name] = field.origin_column
                    elif field.origin_column_type == 'fixed_ref':
                        vals[field.field_id.name] = int(field.origin_column)
                    elif field.origin_column_type == 'formula':
                        pass
                    elif field.origin_column_type == 'm2o_external_code':
                        origin_v, target_f = field.origin_column.split(',')
                        origin_value = row.get(origin_v)
                        if origin_value:
                            existing_rel = self.env[field.field_id.relation].search([(target_f, '=', row[origin_v])])
                            if existing_rel:
                                vals[field.field_id.name] = existing_rel[0].id
                            else:
                                vals[field.field_id.name] = False
                        else:
                            vals[field.field_id.name] = False
                    elif field.origin_column_type == 'fixed_m2o':
                        target_model = self.env[field.field_id.relation]
                        # Utiliza 'field.field_mrelated' para especificar el campo por el cual buscar, por defecto 'id'
                        target_field = field.field_mrelated or 'id'
                        existing_rel = target_model.search([(target_field, '=', field.origin_column)], limit=1)
                        if existing_rel:
                            vals[field.field_id.name] = existing_rel.id
                        else:
                            _logger.error(f"Registro no encontrado en {field.field_id.relation} donde {target_field} = {field.origin_column}")
                            self.message_post(body=f"Registro no encontrado en {field.field_id.relation} donde {target_field} = {field.origin_column}")
                            if not self.allow_parcial_transaction:
                                raise exceptions.UserError(f"Registro no encontrado en {field.field_id.relation} donde {target_field} = {field.origin_column}")
                            else:
                                vals[field.field_id.name] = False 
                except Exception as field_error:
                    _logger.error(f"Error al procesar el campo {field.field_id.name}: {str(field_error)}")
                    self.message_post(body=f"Error al procesar el campo {field.field_id.name} para el registro {row}: {str(field_error)}")
                    if not self.allow_parcial_transaction:
                        raise exceptions.UserError(f"Error al procesar el campo {field.field_id.name} para el registro {row}: {str(field_error)}")

            unique_constraints = self.env[self.model_id.model]._sql_constraints
            _logger.info(f"Restricciones únicas encontradas: {unique_constraints}")

            for constraint in unique_constraints:
                constraint_name, constraint_fields, _ = constraint

                constraint_field_list = [field.strip() for field in constraint_fields.replace('unique (', '').replace(')', '').split(',')]
                _logger.info(f"Campos de la restricción única: {constraint_field_list}")
                if len(constraint_field_list) > 1:
                    last_field = constraint_field_list[-1]

                    if last_field in vals:
                        domain = [(field, '=', vals[field]) for field in constraint_field_list]
                        existing_record = self.env[self.model_id.model].search(domain, limit=1)
                        _logger.info(f"Registro existente encontrado: {existing_record}")

                        if existing_record:
                            existing_record.write({last_field: f"{existing_record[last_field]}_old_{existing_record.id}"})
                            _logger.info(f"Modificando campo '{last_field}' en registro existente con ID {existing_record.id}")
            existing_record = self.env[self.model_id.model].search([(self.target_external_id.name, '=', row[self.origin_primary_key])])

            try:
                with self.env.cr.savepoint():
                    if existing_record:
                        existing_record.write(vals)
                        print("REESCRRIBIENDO////////////////////////////",existing_record,"///")
                    else:
                        self.env[self.model_id.model].create(vals)
                        print("CREEAANDOOOOO////////////////////////////",existing_record,"///")

            except Exception as e:
                _logger.error(f"Error Saving data {row}: {str(e)}")
                self.message_post(body=f"Error Saving data {row}: {str(e)}")
                
                if not self.allow_parcial_transaction:
                    raise exceptions.UserError(f"Error Saving data {row}: {str(e)}")
        
        self.message_post(body="Successful data migration")

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': 'Your data migration was successful!',
                'sticky': False,
                'type': 'success',
            },
        }

    def button_sync_data2(self):
        self.ensure_one()

        headers, rows = self.data_source_id.execute_query(self.query)

        data_rows = [dict(zip(headers, row_data)) for row_data in rows]

        origin_primary_keys = [row[self.origin_primary_key] for row in data_rows]

        existing_records = self.env[self.model_id.model].search([
            (self.target_external_id.name, 'in', origin_primary_keys)
        ])
        existing_records_dict = {rec[self.target_external_id.name]: rec for rec in existing_records}

        m2o_fields = [field for field in self.field_ids if field.origin_column_type == 'm2o_external_code']
        related_models_data = {}
        for field in m2o_fields:
            origin_v, target_f = field.origin_column.split(',')
            related_values = set(row[origin_v] for row in data_rows)
            existing_rels = self.env[field.field_id.relation].search([(target_f, 'in', list(related_values))])
            related_models_data[field.field_id.relation] = {
                rel[target_f]: rel.id for rel in existing_rels
            }

        records_to_create = []
        records_to_update = []

        for row in data_rows:
            vals = {}
            vals[self.target_external_id.name] = row[self.origin_primary_key]

            for field in self.field_ids:
                try:
                    field_name = field.field_id.name
                    if field.origin_column_type == 'column':
                        value = row.get(field.origin_column)
                        if field.field_ttype in ['date', 'datetime']:
                            vals[field_name] = value if value else None
                        else:
                            vals[field_name] = value if value not in [None, ''] else ''
                    elif field.origin_column_type == 'column_int':
                        vals[field_name] = int(row[field.origin_column]) if row[field.origin_column] else 0
                    elif field.origin_column_type == 'column_float':
                        vals[field_name] = float(row[field.origin_column]) if row[field.origin_column] else 0.0
                    elif field.origin_column_type == 'column_m2m':
                        ids_list = ast.literal_eval(field.origin_column)
                        vals[field_name] = [(6, 0, ids_list)]
                    elif field.origin_column_type == 'fixed':
                        vals[field_name] = field.origin_column
                    elif field.origin_column_type == 'fixed_ref':
                        vals[field_name] = int(field.origin_column)
                    elif field.origin_column_type == 'formula':
                        pass  
                    elif field.origin_column_type == 'm2o_external_code':
                        origin_v, target_f = field.origin_column.split(',')
                        related_data = related_models_data.get(field.field_id.relation, {})
                        vals[field_name] = related_data.get(row[origin_v], False)
                    elif field.origin_column_type == 'fixed_m2o':
                        target_model = self.env[field.field_id.relation]
                        target_field = field.field_mrelated or 'id'
                        existing_rel = target_model.search([(target_field, '=', field.origin_column)], limit=1)
                        if existing_rel:
                            vals[field_name] = existing_rel.id
                        else:
                            _logger.error(f"Registro no encontrado en {field.field_id.relation} donde {target_field} = {field.origin_column}")
                            # self.message_post(body=f"Registro no encontrado en {field.field_id.relation} donde {target_field} = {field.origin_column}")
                            if not self.allow_parcial_transaction:
                                raise exceptions.UserError(f"Registro no encontrado en {field.field_id.relation} donde {target_field} = {field.origin_column}")
                            else:
                                vals[field_name] = False
                except Exception as field_error:
                    _logger.error(f"Error al procesar el campo {field_name}: {str(field_error)}")
                    # self.message_post(body=f"Error al procesar el campo {field_name} para el registro {row}: {str(field_error)}")
                    if not self.allow_parcial_transaction:
                        raise exceptions.UserError(f"Error al procesar el campo {field_name} para el registro {row}: {str(field_error)}")

            origin_key = row[self.origin_primary_key]
            existing_record = existing_records_dict.get(origin_key)

            try:
                if existing_record:
                    _logger.info(f"Actualizando registro existente con ID {existing_record.id}")
                    existing_record.with_context(syncing_data=True).write(vals)
                else:
                    _logger.info(f"Creando nuevo registro con valores {vals}")
                    records_to_create.append(vals)
            except Exception as e:
                _logger.error(f"Error al procesar el registro {row}: {str(e)}")
                # self.message_post(body=f"Error al procesar el registro {row}: {str(e)}")
                if not self.allow_parcial_transaction:
                    raise exceptions.UserError(f"Error al procesar el registro {row}: {str(e)}")

        if records_to_create:
            try:
                with self.env.cr.savepoint():
                    _logger.info(f"Creando registros en lote: {records_to_create}")
                    self.env[self.model_id.model].create(records_to_create)
            except Exception as e:
                _logger.error(f"Error al crear registros: {str(e)}")
                # self.message_post(body=f"Error al crear registros: {str(e)}")
                if not self.allow_parcial_transaction:
                    raise exceptions.UserError(f"Error al crear registros: {str(e)}")

        self.message_post(body="Successful data migration")

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': 'Your data migration was successful!',
                'sticky': False,
                'type': 'success',
            },
        }


    def action_show_query_result(self):
        self.ensure_one()

        headers, rows = self.data_source_id.execute_query(self.query + " limit 50")

        table_html = self._generate_html_table(headers, rows)

        self.result = table_html

    def _generate_html_table(self, headers, rows):
        table_html = "<table border='1' class='o_list_table table table-sm table-hover position-relative table-striped'>"

        table_html += "<thead><tr>"
        for header in headers:
            table_html += f"<th>{header}</th>"
        table_html += "</tr></thead>"

        table_html += "<tbody>"
        for row in rows:
            table_html += "<tr>"
            for cell in row:
                table_html += f"<td>{cell}</td>"
            table_html += "</tr>"
        table_html += "</tbody>"
        
        table_html += "</table>"
        return table_html
    
    def export_data_targets_button(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/dv/export_data_targets?ids=%s' % ','.join(map(str, self.ids)),
            'target': 'self',
        }

    @api.model
    def data_import_dv(self, ks_result):
        try:
            data = json.loads(ks_result)
            for target_data in data:
                data_source = self.env['dv.data.source'].search([('name', '=', target_data['data_source_id'])], limit=1)
                target_external_id = self.env['ir.model.fields'].search([('name', '=', target_data['target_external_id'])], limit=1)  
                model_id = self.env['ir.model'].search([('model', '=', target_data['model_id'])], limit=1)
                model_dv_id = self.env['dv.model.lines'].search([('name', '=', target_data['model_dv_id'])], limit=1)
                
                if not data_source or not target_external_id or not model_id:
                    raise ValidationError(_("One or more references could not be found during the import."))

                target = self.create({
                    'name': target_data['name'],
                    'sequence': target_data['sequence'],
                    'tdone': target_data['tdone'],
                    'color': target_data['color'],
                    'method': target_data['method'],
                    'model_dv_id': model_dv_id.id,
                    'active_c_xmlrpc': target_data['active_c_xmlrpc'],
                    'data_source_id': data_source.id,
                    'query': target_data['query'],
                    'allow_parcial_transaction': target_data['allow_parcial_transaction'],
                    'origin_primary_key': target_data['origin_primary_key'],
                    'target_external_id': target_external_id.id,
                    'model_id': model_id.id,
                    'field_ids': [(0, 0, {
                        'origin_column': field['origin_column'],
                        'origin_column_type': field['origin_column_type'],
                        'field_id': self.env['ir.model.fields'].search([('name', '=', field['field_id']), ('model_id', '=', model_id.id)], limit=1).id,                    
                    }) for field in target_data.get('fields', [])],
                    'field_noalma_ids': [(0, 0, {
                        'origin_column': field.get('origin_column', ''),
                        'origin_column_type': field.get('origin_column_type', ''),
                        'field_id': self.env['ir.model.fields'].search([
                            ('name', '=', field['field_id']), 
                            ('model_id', '=', model_id.id)
                        ], limit=1).id,                    
                    }) for field in target_data.get('field_noalma_fields', [])],      
                    'note': target_data['note'],              
                })
            return True
        except Exception as e:
            _logger.warning("Error importing data: %s", e)
            raise ValidationError(_("There was an error importing the data: %s" % e))


    def action_delete_chatter(self):
        self.ensure_one()
        messages = self.env['mail.message'].search([
            ('res_id', '=', self.id),
            ('model', '=', self._name),
        ])
        messages.unlink()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
    
