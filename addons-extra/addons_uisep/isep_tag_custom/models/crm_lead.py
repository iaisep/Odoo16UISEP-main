from odoo import api, fields, models


class CrmLead(models.Model):
    _inherit = "crm.lead"

    @api.model
    def create(self, vals):
        lead = super().create(vals)

        email = vals.get('email_from') or lead.email_from
        tag_obj = self.env['crm.tag']

        tag_lead = self.env.ref('isep_tag_custom.tag_lead_01', raise_if_not_found=False)
        tag_alumno = self.env.ref('isep_tag_custom.tag_lead_02', raise_if_not_found=False)
        tag_alumno_activo = self.env.ref('isep_tag_custom.tag_lead_03', raise_if_not_found=False)
        tag_alumno_baja = self.env.ref('isep_tag_custom.tag_lead_04', raise_if_not_found=False)

        tag_to_set = tag_lead  

        student = self.env['op.student'].search([('email', '=', email)], limit=1)
        if student:
            if student.status_student == 'valid':
                tag_to_set = tag_alumno_activo
            elif student.status_student == 'graduate':
                tag_to_set = tag_alumno
            elif student.status_student == 'low':
                tag_to_set = tag_alumno_baja

        alumno_tags = [t for t in [tag_lead, tag_alumno, tag_alumno_activo, tag_alumno_baja] if t]
        # Quitar tags de estado anteriores
        for t in alumno_tags:
            if t and t in lead.tag_ids:
                lead.tag_ids = [(3, t.id)]


        if tag_to_set and tag_to_set not in lead.tag_ids:
            lead.tag_ids = [(4, tag_to_set.id)]

        if vals.get('stage_id'):
            stage = self.env['crm.stage'].browse(vals['stage_id'])
            if stage.tag_crm_id:
                lead.tag_ids = [(4, stage.tag_crm_id.id)]

        if vals.get('x_studio_programa_academico'):
            product = self.env['product.template'].browse(vals['x_studio_programa_academico'])
            course = self.env['op.course'].search([
                ('product_template_id', '=', product.id)
            ], limit=1)

            tags_to_add = []
            if product.tag_crm_id:
                tags_to_add.append(product.tag_crm_id)
                tags_to_add.append(product.tag_crm_id_interes)
            if course and course.course_type_id.tag_crm_id:
                tags_to_add.append(course.course_type_id.tag_crm_id)
            if course and course.area_id.tag_crm_id:
                tags_to_add.append(course.area_id.tag_crm_id)

            tag_commands = [
                (4, tag.id) for tag in tags_to_add
                if tag and tag not in lead.tag_ids
            ]
            if tag_commands:
                lead.tag_ids = tag_commands

        return lead


    def write(self, vals):
        for lead in self:
            old_stage = lead.stage_id
            old_program = lead.x_studio_programa_academico
            old_type_tag = None
            old_area_tag = None
            old_type_tag_confirm = None
            old_area_tag_confirm = None

            # Obtener los tags antiguos
            if old_program:
                old_course = self.env['op.course'].search([
                    ('product_template_id', '=', old_program.id)
                ], limit=1)
                if old_course:
                    if old_course.course_type_id.tag_crm_id:
                        old_type_tag = old_course.course_type_id.tag_crm_id
                    if old_course.area_id.tag_crm_id:
                        old_area_tag = old_course.area_id.tag_crm_id
                    if hasattr(old_course.course_type_id, 'tag_crm_id_confirm') and old_course.course_type_id.tag_crm_id_confirm:
                        old_type_tag_confirm = old_course.course_type_id.tag_crm_id_confirm
                    if hasattr(old_course.area_id, 'tag_crm_id_confirm') and old_course.area_id.tag_crm_id_confirm:
                        old_area_tag_confirm = old_course.area_id.tag_crm_id_confirm

            res = super(CrmLead, lead).write(vals)

            tag_commands = []

            # Etapa y programa nuevos
            new_stage = self.env['crm.stage'].browse(vals['stage_id']) if 'stage_id' in vals else lead.stage_id
            new_program = self.env['product.template'].browse(vals['x_studio_programa_academico']) if 'x_studio_programa_academico' in vals else lead.x_studio_programa_academico

            new_type_tag = None
            new_type_tag_confirm = None
            new_area_tag = None
            new_area_tag_confirm = None
            if new_program:
                course = self.env['op.course'].search([
                    ('product_template_id', '=', new_program.id)
                ], limit=1)
                if course:
                    if course.course_type_id.tag_crm_id:
                        new_type_tag = course.course_type_id.tag_crm_id
                    if hasattr(course.course_type_id, 'tag_crm_id_confirm') and course.course_type_id.tag_crm_id_confirm:
                        new_type_tag_confirm = course.course_type_id.tag_crm_id_confirm
                    if course.area_id.tag_crm_id:
                        new_area_tag = course.area_id.tag_crm_id
                    if hasattr(course.area_id, 'tag_crm_id_confirm') and course.area_id.tag_crm_id_confirm:
                        new_area_tag_confirm = course.area_id.tag_crm_id_confirm

            was_won = old_stage.is_won
            is_won = new_stage.is_won

            tag_lead = self.env.ref('isep_tag_custom.tag_lead_01', raise_if_not_found=False)
            tag_alumno = self.env.ref('isep_tag_custom.tag_lead_02', raise_if_not_found=False)
            tag_alumno_activo = self.env.ref('isep_tag_custom.tag_lead_03', raise_if_not_found=False)
            tag_alumno_baja = self.env.ref('isep_tag_custom.tag_lead_04', raise_if_not_found=False)
            alumno_tags_ids = [x.id for x in [tag_lead, tag_alumno, tag_alumno_activo, tag_alumno_baja] if x]

            if was_won is False and is_won is True:

                for tid in alumno_tags_ids:
                    if tid and tid in lead.tag_ids.ids:
                        tag_commands.append((3, tid))
                if tag_alumno_activo and tag_alumno_activo.id not in lead.tag_ids.ids:
                    tag_commands.append((4, tag_alumno_activo.id))

            if old_program and 'x_studio_programa_academico' in vals:
                for tag in [old_program.tag_crm_id, old_program.tag_crm_id_confirm, old_program.tag_crm_id_interes]:
                    if tag and tag in lead.tag_ids:
                        tag_commands.append((3, tag.id))
                for tag in [old_type_tag, old_type_tag_confirm, old_area_tag, old_area_tag_confirm]:
                    if tag and tag in lead.tag_ids:
                        tag_commands.append((3, tag.id))

            if old_program:
                if was_won is False and is_won is True:
                    for tag, tag_confirm in [
                        (old_program.tag_crm_id, old_program.tag_crm_id_confirm),
                        (old_type_tag, old_type_tag_confirm),
                        (old_area_tag, old_area_tag_confirm),
                    ]:
                        if tag and tag in lead.tag_ids:
                            tag_commands.append((3, tag.id))
                        if tag_confirm and tag_confirm not in lead.tag_ids:
                            tag_commands.append((4, tag_confirm.id))
                    if old_program.tag_crm_id_interes and old_program.tag_crm_id_interes in lead.tag_ids:
                        tag_commands.append((3, old_program.tag_crm_id_interes.id))
                if was_won is True and is_won is False:
                    for tag, tag_confirm in [
                        (old_program.tag_crm_id, old_program.tag_crm_id_confirm),
                        (old_type_tag, old_type_tag_confirm),
                        (old_area_tag, old_area_tag_confirm),
                    ]:
                        if tag_confirm and tag_confirm in lead.tag_ids:
                            tag_commands.append((3, tag_confirm.id))
                        if tag and tag not in lead.tag_ids:
                            tag_commands.append((4, tag.id))
                    if old_program.tag_crm_id_interes and old_program.tag_crm_id_interes not in lead.tag_ids:
                        tag_commands.append((4, old_program.tag_crm_id_interes.id))

            # AGREGAR NUEVOS TAGS del nuevo programa según etapa actual
            if new_program and 'x_studio_programa_academico' in vals:
                if not new_stage.is_won:
                    tags_to_add = [
                        new_program.tag_crm_id,
                        new_program.tag_crm_id_interes,
                        new_type_tag,
                        new_area_tag,
                    ]
                else:
                    tags_to_add = [
                        new_program.tag_crm_id_confirm,
                        new_type_tag_confirm,
                        new_area_tag_confirm,
                    ]
                for tag in tags_to_add:
                    if tag and tag not in lead.tag_ids:
                        tag_commands.append((4, tag.id))

            # CAMBIO DE ETAPA (sin cambio de programa): tags de etapa
            if 'stage_id' in vals and not 'x_studio_programa_academico' in vals:
                if old_stage.tag_crm_id and old_stage.tag_crm_id in lead.tag_ids:
                    tag_commands.append((3, old_stage.tag_crm_id.id))
                if new_stage.tag_crm_id and new_stage.tag_crm_id not in lead.tag_ids:
                    tag_commands.append((4, new_stage.tag_crm_id.id))

            if tag_commands:
                lead.tag_ids = tag_commands

        return res

    def _sync_tags_to_partner(self):
        for lead in self:
            partner = lead.partner_id
            if not partner:
                continue

            lead_crm_codes = set(
                tag.partner_tags_id.code if tag.partner_tags_id else tag.code
                for tag in lead.tag_ids
            )
            #print(f"///////Tag codes CRM DESEADAS: {lead_crm_codes}")

            partner_cats = partner.custom_tag_id
            partner_cat_codes = set(partner_cats.mapped('code'))
            #print(f"///////Categorías actuales del partner: {[cat.name for cat in partner_cats]}")

            codes_to_add = lead_crm_codes - partner_cat_codes
            codes_to_remove = partner_cat_codes - lead_crm_codes

            cats_to_add = self.env['res.partner.tags'].search([('code', 'in', list(codes_to_add))])
            cats_to_remove = partner_cats.filtered(lambda c: c.code in codes_to_remove)

            #print(f"///////Categorías CRM a AGREGAR: {[cat.name for cat in cats_to_add]}")
            #print(f"///////Categorías CRM a QUITAR: {[cat.name for cat in cats_to_remove]}")

            final_cats = (partner_cats | cats_to_add) - cats_to_remove
            #print(f"///////Categorías finales a asignar al partner: {[cat.name for cat in final_cats]}")

            if set(final_cats.ids) != set(partner_cats.ids):
                partner.custom_tag_id = [(6, 0, final_cats.ids)]
