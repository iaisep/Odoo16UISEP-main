/** @odoo-module */
import { kanbanView } from "@web/views/kanban/kanban_view";
import { registry } from "@web/core/registry";
import { KanbanRenderer } from "@web/views/kanban/kanban_renderer";

export class KanbanRendererOnBoarding extends KanbanRenderer {
    updateOnboardingTitle(){
        const records = this.getGroupsOrRecords();
        if(records.length > 0){
            if(records[0] && records[0].record.data.plan_id.length){
                return records[0].record.data.plan_id[1];
            }
        }
        return false;
    }
}

KanbanRendererOnBoarding.template = 'web.KanbanRendererOnBoarding'

registry.category("views").add('no_search_panel_onboarding', {
     ...kanbanView,
     Renderer: KanbanRendererOnBoarding,
     display: {
           controlPanel: false
    },
});
