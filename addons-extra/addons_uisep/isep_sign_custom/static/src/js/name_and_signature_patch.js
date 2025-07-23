/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { NameAndSignature } from "web.name_and_signature"; // Importa la clase legacy

patch(NameAndSignature.prototype, "name_and_signature_patch", {
    setup() {
        this._super();
    },

    init(parent, options) {
        this._super(parent, options);
        options = options || {};
        this.signMode = options.mode || (options.noInputName && !this.defaultName ? 'draw' : 'draw');
    },
});