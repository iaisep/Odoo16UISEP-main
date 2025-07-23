# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class SepReport(models.Model):
    _name = "sep.report"
    _description = "Sep Report Annex 9"
    _auto = False
    _rec_name = 'curp'
    _order = 'curp asc'

    admission_status = fields.Selection([('ins','Inscripción'),('reins','Reinscripción')], string="Estatus", readonly=True)
    academic_year = fields.Char(string='Año del ciclo escolar', readonly=True)
    curp = fields.Char(string='Curp', readonly=True)
    avg_score = fields.Float(string="Promedio General")
    certificate_type = fields.Selection([('ct','Certificado Total'),('cp','Certificado Parcial'),('tp','Título Profesional'),('dp','Diploma'),('gr','Grado')], string="Tipo de Certficado")
    
    expedition_date = fields.Char(string="Fecha de expedición del documento")
    document_no = fields.Char(string="Folio del documento")
    
    student_id = fields.Many2one('op.student', string="Estudiante", readonly=True)

    def _with_sep_report(self):
        return ""

    def _select_sep_report(self):
        select_ = f"""
            MIN(l.id) AS id,
            COUNT(*) AS nbr,
            s.id AS student_id,
            a.admission_status AS admission_status,
            batch.academic_year as academic_year,
            partner.l10n_mx_edi_curp as curp,
            l.avg_score as avg_score,
            s.certificate_type AS certificate_type,
            NULL AS expedition_date,
            NULL AS document_no
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

    def _from_sep_report(self):
        res= """
            app_gradebook_student l
            LEFT JOIN op_batch batch on l.batch_id = batch.id
            LEFT JOIN op_admission a on l.admission_id = a.id
            LEFT JOIN op_student s on a.student_id = s.id
            LEFT JOIN res_partner partner on s.partner_id = partner.id
            """
        return res

    def _where_sep_report(self):
        return """
            s.annex_9 IS TRUE """

    def _group_by_sep_report(self):
        return """
            s.id,
            a.admission_status,
            batch.academic_year,
            partner.l10n_mx_edi_curp, 
            l.avg_score,
            s.certificate_type,
            expedition_date,
            document_no
            """

    def _query(self):
        with_ = self._with_sep_report()
        res = f"""
            SELECT {self._select_sep_report()}
            FROM {self._from_sep_report()}
            WHERE {self._where_sep_report()}
            GROUP BY {self._group_by_sep_report()}
        """
        return res 

    @property
    def _table_query(self):
        res = self._query()
        return res
