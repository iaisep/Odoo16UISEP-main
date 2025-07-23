odoo.define('openeducat_lms.expand_screen', function(require){
    'use strict';

    var Dialog = require('web.Dialog');
    var utils = require('web.utils');
    const {setCookie,getCookie} = require('web.utils.cookies');

    $(document).ready(function () {
        $('.fullscreenwidget').click(function(){
            $('#material_view').toggleClass("fullscreen main-screen");
            if($('#material_view').length && window.location.pathname.startsWith('/course')){
                $('#wrapwrap').toggleClass('active');
                $('.lms_course_sidebar').toggleClass('active');
            }
            setCookie('lms_full', $('#material_view').hasClass('fullscreen') ? 'full': 'sidebar')
            if($('#material_view').hasClass('fullscreen')){
                $('.lms_sidebar_enable').css('padding-left', '0px');
                $('.lms_sidebar_enable').addClass('lms_sidebar_disable');
                $('.lms_sidebar_enable').removeClass('lms_sidebar_enable');

            }else{
                $('.lms_sidebar_disable').css('padding-left', '350px');
                $('.lms_sidebar_disable').addClass('lms_sidebar_enable');
                $('.lms_sidebar_disable').removeClass('lms_sidebar_disable');
            }
        });
        if($('#material_view').length && window.location.pathname.startsWith('/course')){
            // $('#wrapwrap').addClass('lms_sidebar_enable');
             if(getCookie('lms_full') == 'full'){
                 $('#wrapwrap').addClass('active')
             }
        }
        $('.course-thumbnail.detail-page').click( function(){
            if($('.course-thumbnail.detail-page > a').children().is('img')){
                return;
            }
            var $content = $('.course-thumbnail > a').clone();
            if($content.children().is('video')){
                $content.find('video').attr('controls', 'controls');
            }
            if($content.find('iframe').length){
                $content.find('iframe').removeClass('d-none');
                $content.find('iframe').css({
                    height: '100%',
                    width: '100%',
                });
                $content.find('img').addClass('d-none');
            }
            var dialog = new Dialog(null, {
                title: $('.course-detail-h2.course_name').text(),
                size: 'large',
                $content: $content.html(),
                buttons: [],
            }).open();
            dialog.opened().then(function () {
                dialog.$modal.find('.modal-content').css({
                    height: '100%',
                    width: '100%',
                });
            });
        });
    });

});
