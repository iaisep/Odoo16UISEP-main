# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class StudentReport(models.Model):
    _name = "student.report"
    _description = "Student Analysis Report"
    _auto = False
    _rec_name = 'date'
    _order = 'date desc'

    @api.model
    def _get_done_states(self):
        return ['sale', 'done']

    application_number = fields.Char(string='Matricula Institucional', readonly=True)
    academic_year = fields.Char(string='Año del ciclo escolar', readonly=True)
    admission_status = fields.Selection([('ins','Inscripción'),('reins','Reinscripción')], string="Estatus", readonly=True)
    first_name = fields.Char(string='Nombre del Alumno', readonly=True,  translate=True)
    middle_name = fields.Char(string='Primer Apellido', readonly=True, translate=True)
    last_name = fields.Char(string='Segundo Apellido', readonly=True, translate=True)
    curp = fields.Char(string='Curp', readonly=True)
    gender = fields.Char(string='Género', readonly=True)
    date = fields.Char(string='Fecha de Nacimiento', readonly=True)
    student_id = fields.Many2one('op.student', string="Estudiante", readonly=True)
    lang = fields.Selection(related="student_id.lang", string="Idioma/Lengua")
    nationality = fields.Many2one('res.country', string="Pais de Procedencia", readonly=True)
    partner_id = fields.Many2one('res.partner', string="Compañero", readonly=True)
    user_id = fields.Many2one('res.users', string="Usuario", readonly=True)
    company_type = fields.Selection([('fuisep','FUISEP'),('uisep','UISEP')], string="Tipo de Empresa")
    scholar_year = fields.Char(string="Año Escolar", readonly=True)
    special_needs = fields.Selection([('na','No Aplica'),('disabled','Con discapacidad'),('outstanding','Con aptitudes sobresalientes')],string="Necesidades Educativas Especiales", readonly=True)
    cct = fields.Selection([('si','Si'),('no','No'),('no_aplica','No Aplica')], string="CCT", readonly=True)
    academic_background = fields.Selection([('si','Si'),('no','No'),('no_aplica','No Aplica')], string="Presenta Antecedentes Académicos", readonly=True)
    career_key = fields.Char(string="Clave de Carrera", readonly=True)
    institute_key = fields.Char(string="Clave de Institución", readonly=True)
    rvoe_number = fields.Char(string="Número de RVOE", readonly=True)
    rvoe_date = fields.Char(string="Fecha de RVOE", readonly=True)
    educational_mod = fields.Selection([('escolar','Escolar'),('no_escolar','No Escolarizada'),('mixta','Mixta')], string="Modalidad Educativa", readonly=True)
    shift_type = fields.Selection([('matutino','Matutino'),('vespertino','Vespertino'),('mixto','Mixto')], string="Turno", readonly=True)
    education_level = fields.Selection([('profesional','Profesional Asociado'),('tecnico','Técnico Superior Universitario'),('licenciatura','Licenciatura'),('especialidad','Especialidad'),('maestria','Maestria'),('doctorado','Doctorado')], string="Nivel Educativo", readonly=True)
 

    def _with_student(self):
        return ""

    def _select_student(self):
        select_ = f"""
            MIN(a.id) AS id,
            COUNT(*) AS nbr,
            s.id AS student_id,
            batch.company_type as company_type,
            batch.scholar_year as scholar_year,
            batch.cct as cct,
            batch.educational_mod as educational_mod,
            batch.shift_type as shift_type,
            batch.academic_year as academic_year,
            a.application_number as application_number,
            a.admission_status as admission_status,
            a.academic_background as academic_background,
            a.special_needs as special_needs,
            s.first_name AS first_name,
            s.middle_name AS middle_name,
            s.last_name AS last_name,
            TO_CHAR(s.birth_date, 'YYYYMMDD') AS date,
            s.gender AS gender,
            s.partner_id AS partner_id,
            s.user_id AS user_id,
            s.nationality AS nationality,
            course.education_level as education_level,
            course.career_key as career_key,
            course.institute_key as institute_key,
            course.rvoe_number as rvoe_number,
            REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(
            TO_CHAR(course.rvoe_date, 'DD "de" Month "de" YYYY'),
            'January', 'Enero'), 'February', 'Febrero'), 'March', 'Marzo'), 'April', 'Abril'),
            'May', 'Mayo'), 'June', 'Junio'), 'July', 'Julio'), 'August', 'Agosto'),
            'September', 'Septiembre'), 'October', 'Octubre'), 'November', 'Noviembre'), 'December', 'Diciembre') AS rvoe_date,
            partner.l10n_mx_edi_curp as curp
            """

        additional_fields_info = self._select_additional_fields()
        template = """,
            %s AS %s"""
        for fname, query_info in additional_fields_info.items():
            select_ += template % (query_info, fname)

        return select_

    def _case_value_or_one(self, value):
        return f"""CASE COALESCE({value}, 0) WHEN 0 THEN 1.0 ELSE {value} END"""

    def _select_additional_fields(self):
        """Hook to return additional fields SQL specification for select part of the table query.

        :returns: mapping field -> SQL computation of field, will be converted to '_ AS _field' in the final table definition
        :rtype: dict
        """
        return {}

    def _from_student(self):
        res= """
            op_admission a
            LEFT JOIN op_student s on a.student_id = s.id
            LEFT JOIN op_batch batch on a.batch_id = batch.id
            LEFT JOIN op_course course on batch.course_id = course.id
            LEFT JOIN res_partner partner ON s.partner_id = partner.id
            LEFT JOIN res_users odoo_user ON s.user_id = odoo_user.id
            """
        return res

    def _where_student(self):
        return """
            course.sepyc_program IS TRUE """

    def _group_by_student(self):
        return """
            batch.company_type,
            batch.scholar_year,
            batch.cct,
            batch.educational_mod,
            batch.shift_type,
            batch.academic_year,
            a.application_number,
            a.admission_status,
            a.academic_background,
            a.special_needs,
            s.first_name,
            s.middle_name,
            s.last_name,
            date,
            s.partner_id,
            s.user_id,
            s.nationality,
            s.gender,
            course.education_level,
            course.career_key,
            course.institute_key,
            course.rvoe_number,
            rvoe_date,
            partner.l10n_mx_edi_curp, 
            s.id"""

    def _query(self):
        with_ = self._with_student()
        res = f"""
            SELECT {self._select_student()}
            FROM {self._from_student()}
            WHERE {self._where_student()}
            GROUP BY {self._group_by_student()}
        """
        return res 

    @property
    def _table_query(self):
        res = self._query()
        return res
