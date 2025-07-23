/** @odoo-module */

import { X2ManyField } from "@web/views/fields/x2many/x2many_field";
import { registry } from "@web/core/registry";

import { CommonSkillsListRenderer } from "./list_renderer";


export class SkillsFieldRenderer extends CommonSkillsListRenderer {
    get groupBy() {
        return 'student_skills_id';
    }

    calculateColumnWidth(column) {
        if (column.name != 'student_skills_id') {
            return {
                type: 'absolute',
                value: '90px',
            }
        }

        return super.calculateColumnWidth(column);
    }
}
SkillsFieldRenderer.template = 'openeducat_skill_enterprise.SkillsListRenderer';

export class FieldSkills extends X2ManyField {
    async onAdd({ context } = {}) {
        const skillTypeId = this.props.record.resId;
        return super.onAdd({
            context: {
                ...context,
                default_student_id: skillTypeId,
            }
        });
    }
}
FieldSkills.components = {
    ...X2ManyField.components,
    ListRenderer: SkillsFieldRenderer,
};

registry.category("fields").add("student_skills", FieldSkills);
