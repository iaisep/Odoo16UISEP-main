from odoo import  fields, models, exceptions, _
import psycopg2
import xmlrpc.client

class dvDataSource(models.Model):
    _name = 'dv.data.source'
    _description = 'Data Source'

    name = fields.Char('Name', required=True)
    host = fields.Char('Host', required=True)
    port = fields.Integer('Port', required=True, default='5432')
    database = fields.Char('Database', required=True)
    user = fields.Char('User', required=True)
    password = fields.Char('Password', required=True)

    activate_xmlrpc=fields.Boolean('Activar XMLRPC', help="Activar si los datos provienen de otro Odoo compatible con xmlrpc")
    url_rpc = fields.Char('URL rpc', required=True,default='URL de odoo a migrar')
    username_rpc=fields.Char('Usuario rpc', required=True, default='Usuario administrador odoo a migrar')
    db_rpc = fields.Char('Database rpc', required=True, default='Nombre Base de datos odoo a migrar')
    password_rpc=fields.Char('Password rpc', required=True, default='Contrasena administrador de odoo a migrar')

    dv_model_lines_ids = fields.One2many('dv.model.lines', 'dv_source_id', string = "Modelos a migrar", required=False, index=True,readonly=False,copy=False )

    def execute_query(self, query):
        self.ensure_one()

        # Connect to PostgreSQL
        conn_params = {
            'dbname': self.database,
            'user': self.user,
            'password': self.password,
            'host': self.host,
            'port': self.port
        }

        # Verificar se a query possui instruções proibidas
        forbidden_statements = ['UPDATE', 'DELETE', 'CREATE', 'ALTER', 'DROP']
        for statement in forbidden_statements:
            if statement in query.upper():
                raise exceptions.UserError(_('Queries containing %s are not allowed for security reasons.') % statement)

        
        try:
            conn = psycopg2.connect(**conn_params)
            cur = conn.cursor()
            cur.execute(query)  # Assuming query is validated and safe from SQL injection
            rows = cur.fetchall()
            headers = [desc[0] for desc in cur.description]
        except Exception as e:
            raise exceptions.UserError(f"Error executing the query: {str(e)}")
        finally:
            conn.close()

        return headers, rows
    
    def call_models_from_remote(self):
        # Establecer conexión con el servidor remoto
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(self.url_rpc))
        uid = common.authenticate(self.db_rpc, self.username_rpc, self.password_rpc, {})
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(self.url_rpc))

        filters = []

        # Campos que queremos obtener
        fields_to_fetch = ['model', 'name', 'state', 'transient']

        # Obtener los registros del modelo ir.model desde el servidor remoto
        remote_models = models.execute_kw(self.db_rpc, uid, self.password_rpc, 
                                          'ir.model', 'search_read', 
                                          [filters], {'fields': fields_to_fetch})

        # Limpiar los registros anteriores si es necesario
        self.dv_model_lines_ids.unlink()

        # Crear los nuevos registros en dv.model.lines
        for remote_model in remote_models:            
            model_name_db = remote_model['model'].replace('.', '_')

            self.env['dv.model.lines'].create({
                'name': remote_model['model'],
                'descrip': remote_model['name'],
                'type': remote_model['state'],
                'model_tran': remote_model['transient'],
                'name_db': model_name_db,
                'dv_source_id': self.id
            })



class dvModelLines(models.Model):
    _name = 'dv.model.lines'

    name=fields.Char(string="Modelo")
    name_db=fields.Char(string="Modelo en db")
    descrip=fields.Char(string="Descripcion")
    type=fields.Char(string="Tipo")
    model_tran=fields.Boolean(string="Modelo transitorio")
    dv_source_id = fields.Many2one('dv.data.source', string='data source',requerid=True, ondelete="cascade", index=True)