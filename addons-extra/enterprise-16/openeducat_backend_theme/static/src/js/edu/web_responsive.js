/** @odoo-module **/
/* Copyright 2018 Tecnativa - Jairo Llopis
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl). */

// odoo.define("web_responsive", function (require) {
//     "use strict";

    const config = require("web.config");
    const core = require("web.core");
    import { patch } from 'web.utils';
    const FormRenderer = require("web.FormRenderer");
    //const Menu = require("web.Menu");
    const RelationalFields = require("web.relational_fields");
    import { ControlPanel } from "@web/search/control_panel/control_panel";
    const CalendarRenderer = require("web.CalendarRenderer");
    const {QWeb,useState} = owl;
    const Context = require('web.Context');
    import dom from 'web.dom';
    const _t = core._t;
    // const {useState, useContext} = owl.hooks;
    const utils = require('web.utils');
    import {useContext } from "@web/core/utils/hooks";
    import { SearchPanel } from "@web/search/search_panel/search_panel";
    //const SearchPanel = require("@web/static/src/search/search_panel/search_panel.js");
    const ListRenderer = require("web.ListRenderer");


    RelationalFields.FieldStatus.include({
        _setState: function () {
            this._super.apply(this, arguments);
            if (config.device.isMobile) {
                _.map(this.status_information, (value) => {
                    value.fold = true;
                });
            }
        },
    });

    // Sticky Column Selector
    ListRenderer.include({
        _renderView: function () {
            const self = this;
            return this._super.apply(this, arguments).then(() => {
                const $col_selector = self.$el.find(
                    ".o_optional_columns_dropdown_toggle"
                );
                if ($col_selector.length !== 0) {
                    const $th = self.$el.find("thead>tr:first>th:last");
                    $col_selector.appendTo($th);
                }
            });
        },

        _onToggleOptionalColumnDropdown: function (ev) {
            // FIXME: For some strange reason the 'stopPropagation' call
            // in the main method don't work. Invoking here the same method
            // does the expected behavior... O_O!
            // This prevents the action of sorting the column from being
            // launched.
            ev.stopPropagation();
            this._super.apply(this, arguments);
        },
    });
    FormRenderer.include({
        _renderHeaderButtons: function () {
            const $buttons = this._super.apply(this, arguments);
            if (
                !config.device.isMobile ||
                !$buttons.is(":has(>:not(.o_invisible_modifier))")
            ) {
                return $buttons;
            }

            $buttons.addClass("dropdown-menu");
            const $dropdown = $(
                core.qweb.render("web_responsive.MenuStatusbarButtons")
            );
            $buttons.addClass("dropdown-menu").appendTo($dropdown);
            return $dropdown;
        },
    });


    CalendarRenderer.include({
        _getFullCalendarOptions: function () {
            var options = this._super.apply(this, arguments);
            if (config.device.isMobile) {
                options.views.dayGridMonth.columnHeaderFormat = "ddd";
            }
            return options;
        },
    });

    const deviceContext = new Context({
        isMobile: config.device.isMobile,
        size_class: config.device.size_class,
        SIZES: config.device.SIZES,
    });

    window.addEventListener(
        "resize",
        _.debounce(() => {
            const state = deviceContext.state;
            if(state){
                if (state.isMobile !== config.device.isMobile) {
                    state.isMobile = !state.isMobile;
                }
                if (state.size_class !== config.device.size_class) {
                    state.size_class = config.device.size_class;
                }
            }
        }, 15)
    );

    patch(ControlPanel, 'openeducat_backend_theme/static/src/js/edu/control_panel.js', {
        constructor() {
            this._super(...arguments);
            this.state = useState({
                mobileSearchMode: "",
            });
            this.device = useContext(deviceContext);
        }
    });

    patch(SearchPanel, "web_responsive.SearchPanelMobile", {
        constructor() {
            this._super(...arguments);
            this.state.mobileSearch = false;
            this.device = useContext(deviceContext);
        },
        getActiveSummary() {
            const selection = [];
            for (const filter of this.model.get("sections")) {
                let filterValues = [];
                if (filter.type === "category") {
                    if (filter.activeValueId) {
                        const parentIds = this._getAncestorValueIds(
                            filter,
                            filter.activeValueId
                        );
                        filterValues = [...parentIds, filter.activeValueId].map(
                            (valueId) => filter.values.get(valueId).display_name
                        );
                    }
                } else {
                    let values = [];
                    if (filter.groups) {
                        values = [
                            ...filter.groups.values().map((g) => g.values),
                        ].flat();
                    }
                    if (filter.values) {
                        values = [...filter.values.values()];
                    }
                    filterValues = values
                        .filter((v) => v.checked)
                        .map((v) => v.display_name);
                }
                if (filterValues.length) {
                    selection.push({
                        values: filterValues,
                        icon: filter.icon,
                        color: filter.color,
                        type: filter.type,
                    });
                }
            }
            return selection;
        }
    });
