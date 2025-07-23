odoo.define('openeducat_digital_library.my_library', function (require) {
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

    var MyLibraryWidget = publicWidget.Widget.extend({
        events:{
        'keyup #material_detail_search_box': '_onSearchKeyUp',
        },
        init: function(){
            this._super.apply(this,arguments);
        },
        start: function () {
            return this._super();
        },
        _onSearchKeyUp: function(e){
            var match_value = $('#material_detail_search_box').val();
            if(match_value.includes('Name Like: ')){
                $('#search_box_filter').val('name');
                match_value = match_value.replace('Name Like: ','');
                $('#material_detail_search_box').val(match_value);
                $('#search_box_filter_submit').click();
            }else if(match_value.includes('Author Like: ')){
                $('#search_box_filter').val('author');
                match_value = match_value.replace('Author Like: ','');
                $('#material_detail_search_box').val(match_value);
                $('#search_box_filter_submit').click();
            }else if(match_value.includes('Publisher Like: ')){
                $('#search_box_filter').val('publisher');
                match_value = match_value.replace('Publisher Like: ','');
                $('#material_detail_search_box').val(match_value);
                $('#search_box_filter_submit').click();
            }else if(match_value.includes('Tag Like: ')){
                $('#search_box_filter').val('tag');
                match_value = match_value.replace('Tag Like: ','');
                $('#material_detail_search_box').val(match_value);
                $('#search_box_filter_submit').click();
            }else{
                $('#search_box_values').empty();
                $('#search_box_values').append("<option data-filter='name' value='Name Like: " + match_value + "'>");
                $('#search_box_values').append("<option data-filter='author' value='Author Like: " + match_value + "'>");
                $('#search_box_values').append("<option data-filter='publisher' value='Publisher Like: " + match_value + "'>");
                $('#search_box_values').append("<option data-filter='tag' value='Tag Like: " + match_value + "'>");
            }
        },
    });
//    websiteRootData.websiteRootRegistry.add(MyLibraryWidget, '#my_digital_library_detail');
    publicWidget.registry.MyLibraryWidget = MyLibraryWidget;
    return MyLibraryWidget;
});
