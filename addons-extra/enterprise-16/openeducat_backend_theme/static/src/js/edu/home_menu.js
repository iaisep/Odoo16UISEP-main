/** @odoo-module **/

const { Component, hooks, useState , useExternalListener, useRef } = owl;
// const { useExternalListener, useRef, useState } = owl.hooks;
import { computeAppsAndMenuItems } from "@web/webclient/menus/menu_helpers";
import { fuzzyLookup } from "@web/core/utils/search";
import { browser } from "@web/core/browser/browser";
import { session } from "@web/session";
import { ErrorHandler, NotUpdatable } from "@web/core/utils/components";
import { NavBar, MenuDropdown, MenuItem } from "@web/webclient/navbar/navbar";
import { menuService } from "@web/webclient/menus/menu_service";
import { bus } from 'web.core';

export class HomeMenu extends Component{
    setup() {
        super.setup(...arguments);
        //useListener('keyup', this._onKeuUp)
        bus.trigger('home_menu_change', true);
        useExternalListener(document, 'keydown', this._onKeyUp);
    }

    constructor(...args) {
        super(...args);
        this.searchBox = useRef('searchBox');
        var menus = $.extend(true, {}, this.props.rootMenus);
        var allMenus = $.extend(true, {}, this.props.allMenus);
        this.searchableMenus = {};
        var searchable = this.generateSearchableMenus(allMenus, false);
        //var allMenus = $.extend(true, {}, this.props.allMenus);
        //this.searchableMenus = allMenus;
        this.rootMenus = menus;
        this.state = useState({
            hasSearchResults: false,
            rootMenus: menus,
            searchableMenus: searchable,
            index: 1,
            query: "",
        });
        this.inputEl = $('input');
        this.inputEl.focus();
    }

    generateSearchableMenus( menus, root ) {
        var self = this;
        if(!root){
            for(const [key, value] of Object.entries(menus)){
                if(value.parentId == false){
                    Object.assign(self.searchableMenus, {
                        [value.name.trim()]: value,
                    });
                } else {
                    var rootEl = Object.keys(self.searchableMenus).find(key => self.searchableMenus[key].id == value.parentId);
                    if(rootEl){
                        Object.assign(self.searchableMenus, {
                            [rootEl + "/ " + value.name.trim()]: value,
                        });
                    }
                }
            }
        }
        return self.searchableMenus;
    }

    onMenuClick(currentId) {
        bus.trigger('home_menu_change', false);
        bus.trigger('home_menu_selected', this.props.allMenus[currentId]);
    }

    async _onKeyUp(e) {
        if(!$(document.activeElement).is($('body')) &&  !$(document.activeElement).is($('input.o_search_box'))){
            return;
        }
        if( e.key == 'ArrowDown' || e.key == 'ArrowUp' || e.key == 'Enter'){
            if( e.key == 'ArrowDown'){
                if(this.allList <= this.state.index){ return; }
                if(!this.state.hasSearchResults){ return; }
                this.state.index++;
            } else if( e.key == 'ArrowUp'){
                if(this.state.index <= 1){ return; }
                if(!this.state.hasSearchResults){ return; }
                this.state.index--;
            } else if(e.key == 'Enter'){
                if($('.o-menu-search-result.active').length > 0){
                    bus.trigger('home_menu_change', false);
                    bus.trigger('home_menu_selected', this.props.allMenus[parseInt($('.o-menu-search-result.active').data('menuId'))]);
                }
            }

            $('.o_app_search_results').scrollTo($('.o-menu-search-result.active'), {
                offset: {
                    top: $('.o_app_search_results').height() * -0.5,
                },
            });
        }

        if(!(e.keyCode >= 65 && e.keyCode <= 90)){
            return;
        }
        if(!this.state.hasSearchResults){
            this.state.hasSearchResults = await true;
        }
        if(document.activeElement !== this.searchBox.el) {
            this.searchBox.el.focus();
        }
    }

    _onInputSearch(e) {
        this.updateSearch(this.searchBox.el.value);
    }

    updateSearch(query) {
        var menus = this.props.rootMenus.children;
        this.state.index = 1;
        this.state.rootMenus.children = _.filter(menus, function (app) {
            return app.name.toLowerCase().indexOf(query.toLowerCase()) !== -1;
        });
        var searchableMenus = _.pick(this.searchableMenus, function(value, key){
            return key.toLowerCase().indexOf(query.toLowerCase()) !== -1 && value.actionID !== false;
        });
        this.state.searchableMenus = searchableMenus;
        this.allList = Object.keys(searchableMenus).length;
    }

    onSearchChosen(menu) {
        var self = this;
        bus.trigger('home_menu_change', false);
        bus.trigger('home_menu_selected', this.props.allMenus[menu.id]);
    }

}
HomeMenu.template = 'HomeMenu.Template';
HomeMenu.props = {
    rootMenus: Object,
    allMenus: Object,
};

HomeMenu.components = { NavBar, MenuDropdown, MenuItem, NotUpdatable, ErrorHandler };
