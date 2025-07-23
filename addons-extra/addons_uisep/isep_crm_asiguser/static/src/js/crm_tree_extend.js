/** @odoo-module **/

import { registry } from '@web/core/registry';
import { listView } from '@web/views/list/list_view';
import { ListController } from "@web/views/list/list_controller";
var Dialog = require('web.Dialog');

export class CrmListController extends ListController {
    
    
    setup() {
        super.setup();
    }
   
    OnCrmasigClick() {
     
    var rpc = require('web.rpc');
    rpc.query({
        model: 'crm.lead',
        method: 'action_assign_crm',
        args: [{  }],
    }).then(function (result) {           
        
        if(result==0){
            Dialog.alert(this,"No hay leads para asignar")
                  
        }
        if(result==1){
            Dialog.alert(this,"Se asigno leads correctamente")
            location.reload();
        }
        if(result==2){
            Dialog.alert(this,"Tienes leads asignados, puedes solicitar leads nuevos en cuanto tu carga actual se menor.")
            location.reload();
        }
    

    });
    
    }
 }
 registry.category("views").add("button_crm_tree", {
    ...listView,
    Controller: CrmListController,
    buttonTemplate: "button_crm_assign.ListView.Buttons",
 });