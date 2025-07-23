odoo.define('openeducat_digital_library.script', function (require) {
    "use strict";
    var core = require('web.core');
    var Dialog = require("web.Dialog");
    var session = require('web.session');
    var ajax = require('web.ajax');
    var Widget = require('web.Widget');
    var publicWidget = require('web.public.widget');
    var websiteRootData = require('website.root');
    var utils = require('web.utils');
    var _t = core._t;
    var qweb = core.qweb;
    var wUtils = require('website.utils');

    var LibraryPDFWidget = publicWidget.Widget.extend({
        events:{
            'click .select_filter_menu': '_onFilterSelectClick',
            'click .select_material_type_menu': '_onFilterTypeSelectClick',
            'keyup #search_bar_material_': '_onSearchKeyUp',
        },
        xmlDependencies: ['/openeducat_digital_library/static/src/xml/category_material_template.xml'],

        init: function(){
            this._super.apply(this,arguments);
        },
        start: function () {
            this.$el.find('.category_all_li').trigger('click');
            return this._super();
        },
        _onSearchKeyUp: function(e){
//            var filter_by = $('#material_filter_by').val(),
             var   input_value = $('#search_bar_material_').val(),
                filter = input_value.toUpperCase(),
                list = $('.search_filter_div');
//                filter_type = $('#material_type_filter_by').val();
//            console.log('....',filter_by)
//            filter_type = filter_type.toLowerCase().trim();
//            if(filter_by == ""){
//                filter_by = 'name'
//            }
            for(var i=0; i< list.length; i++){
                var list_value = $(list[i]).data('name');
//                var list_type = $(list[i]).data('type');
//                if(filter_type != 'all' && filter_type != ''){
//                    if (list_value.toUpperCase().indexOf(filter) > -1 && list_type.toLowerCase() == filter_type){
//                        list[i].style.display = "";
//                        } else {
//                          list[i].style.display = "none";
//                    }
//                }else{
                    if (list_value.toUpperCase().indexOf(filter) > -1){
                        list[i].style.display = "";
                        } else {
                          list[i].style.display = "none";
                    }
//                }
            }
        },
        _onFilterSelectClick: function(e){
            var text = $(e.currentTarget).text()
            $('#material_filter_by').attr('value',text.toLowerCase());
            $('#material_filter_by').text(text);
            $('#search_bar_material_').keyup();
        },
        _onFilterTypeSelectClick: function(e){
            var text = $(e.currentTarget).text()
            $('#material_type_filter_by').attr('value',text.toLowerCase());
            $('#material_type_filter_by').text(text);
            $('#search_bar_material_').keyup();
        },
    });
//    websiteRootData.websiteRootRegistry.add(LibraryPDFWidget, '.digital_library_category');
    publicWidget.registry.LibraryPDFWidget = LibraryPDFWidget;
    return LibraryPDFWidget;
});
