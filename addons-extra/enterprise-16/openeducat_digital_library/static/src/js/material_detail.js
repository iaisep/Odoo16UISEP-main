odoo.define('openeducat_digital_library.material_detail', function (require) {
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

    var DigitalMaterialDetailWidget = publicWidget.Widget.extend({
        selector:"#review_course_form",
        events:{
        'click .description_course_click': '_OnDescription',
        'click .review_course_click': '_OnReviewClick',
        'click .star': '_OnStarClick',
        'click #course_review_submit': '_OnReviewSubmit',
        'keyup #material_detail_search_box': '_onSearchKeyUp',
        },
        init: function(){
            this._super.apply(this,arguments);
        },
        start: function () {
            $('.description_show_class').hide();
            $('.review_success_class').hide();
            $('.description_course_click').removeClass('selected_summary_class');
            $('.review_course_click').addClass('selected_summary_class');
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
        _OnDescription: function(e){
            $('.review_show_class').hide();
            $('.review_success_class').hide();
            $('.description_show_class').show();
            $(e.currentTarget).addClass('selected_summary_class');
            $('.review_course_click').removeClass('selected_summary_class');
        },
        _OnReviewClick: function(e){
            $('.description_show_class').hide();
            $('.review_success_class').hide();
            $('.review_show_class').show();
            $(e.currentTarget).addClass('selected_summary_class');
            $('.description_course_click').removeClass('selected_summary_class');
        },
        _OnStarClick:function(e){
            var star_val = $(e.currentTarget).val();
            $('#rating_star_val').attr('value',star_val);
        },
        _OnReviewSubmit: function(e){
            e.stopPropagation();
            e.preventDefault();
            var rating_star = this.$el.find("#rating_star_val").val(),
                review_course_review = this.$el.find('#review_course_review').val(),
                review_name_course = this.$el.find('#review_name_course').val(),
                review_email_course = this.$el.find('#review_email_course').val(),
                material_id = this.$el.find('#material_id_value').val(),
                user_id = session.user_id;
            if(rating_star == '' || review_course_review == '' || review_name_course == '' || review_email_course == ''){
                this.do_notify(_t("Review"), _t("Please Fill Up All The Values."));
            }else{
                ajax.jsonRpc('/digital-library/add-review', 'call', {
                    rating: rating_star,
                    review: review_course_review,
                    name: review_name_course,
                    email: review_email_course,
                    material_id: material_id,
                    user_id:user_id,
                }).then(function(data) {

                });
                $('.review_show_class').hide();
                $('.review_success_class').show();
            }
        },
    });
//    websiteRootData.websiteRootRegistry.add(DigitalMaterialDetailWidget, '#digital_library_material_detail_view');
    publicWidget.registry.DigitalMaterialDetailWidget = DigitalMaterialDetailWidget;
    return DigitalMaterialDetailWidget;
});
