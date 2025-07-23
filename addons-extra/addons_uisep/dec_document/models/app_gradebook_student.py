# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class AppGradebookStudent(models.Model):
    _inherit = "app.gradebook.student"


    def action_export_to_dec(self):

        #New certificates
        new_records = self.env['dec.document']
        for record in self:
            new_lines = self.env['dec.asignatura']
            responsable_id = self.env.company.dec_responsable_id
            if not responsable_id:
                raise ValidationError (_('Se requiere configurar el responsable DEC en ajustes.'))
            total = len([a.id for a in record.course_id.subject_ids.filtered(lambda s: s.subject_type == 'compulsory')]) 
            total_creditos = sum([a.credit_point for a in record.course_id.subject_ids.filtered(lambda s: s.subject_type == 'compulsory')]) 
            certificate_vals = {
                'responsable_id':responsable_id and responsable_id.id or False,

                'ides_ipes':record.course_id.institute_key,
                'id_campus':record.course_id.career_key,
                'rvoe':record.course_id.rvoe_number,
                'fecha_rvoe':record.course_id.rvoe_date,
                'curp_alumno': record.student_id.partner_id.l10n_mx_edi_curp,
                'alumno_nombre': ' '.join([record.student_id.first_name, record.student_id.middle_name]),
                'primer_apellido': record.student_id.last_name and record.student_id.last_name.split()[0],
                'segundo_apellido': record.student_id.last_name and len(record.student_id.last_name.split())>1 and record.student_id.last_name.split()[1] or '',
                'fecha_nacimiento':record.student_id.birth_date,
                'id_genero':record.student_id.gender == 'f' and '250' or '251',
                'programa_estudio':record.course_id.id_carrera,
                'calificacion_minima':record.course_id.calificacion_minima,
                'calificacion_maxima':record.course_id.calificacion_maxima,
                'calificacion_minima_aprobatoria':record.course_id.calificacion_minima_aprobatoria,
                'programa_estudio_tipo':'93',
                'total': total, #Total de asignaturas en el programa de estudios
                'total_creditos': total_creditos, #Total de creditos en el programa de estudios
                'clave_plan':'2020',
                'nivel_estudios':'82',
                'numero_control':record.admission_id.application_number,
                'id_tipo_certificacion':record.state == 'done' and '79' or '80',
                }
            new_certificate = new_records.create(certificate_vals)
            for subject in record.gradebook_subject_ids.filtered(lambda s: s.op_subject_id.subject_type =='compulsory'):
                new_line = new_lines.create({
                    'dec_id':new_certificate.id,
                    'clave_asignatura':subject.op_subject_id.code,
                    'calificacion':subject.final_subject_note,
                    'creditos':1,
                })
            new_records |= new_certificate

        return {
            'name': _('Certificados DEC SEP'),
            'res_model': 'dec.document',
            'view_mode': 'tree,form',
            'context': {
                'active_model': 'dec.document',
                'active_ids': new_records.ids,
            },
            'target': 'self',
            'type': 'ir.actions.act_window',
        }

