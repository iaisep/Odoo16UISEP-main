odoo.define('openeducat_lms.open-modal', function (require) {
    "use strict";

    var core = require('web.core');
    var Dialog = require("web.Dialog");
    var session = require('web.session');
    var ajax = require('web.ajax');
    var Widget = require('web.Widget');
    var publicWidget = require('web.public.widget');
    //var websiteRootData = require('website.root');
    var utils = require('web.utils');
    var _t = core._t;
    var qweb = core.qweb;

    var OpenModalWidget = publicWidget.Widget.extend({
    selector:'.card-body',
    events: {

        'click .preview-btn': '_onClickPreviewButton',
        'click .edit-btn': '_onClickEditButton',
    },

    xmlDependencies: ['/openeducat_lms/static/src/xml/openmodal.xml'],
    init: function () {
        this._super.apply(this, arguments);
    },

    _onClickPreviewButton: function(e){
        var material_id = $(e.currentTarget).data('material-id');
        if (material_id != undefined)
        {
            ajax.jsonRpc('/get/material', 'call',
            {
                'material_id': material_id,
            }).then(function (data) {
                if (data['embed_code'])
                {
                    var embed_code = qweb.render('MaterialDetails',
                    {
                        data: data['embed_code']
                    });
                    $('.modal-title-lms').html(data['name'])
                    $('.modal-body').html(embed_code);
                    $('#preview-modal').modal("show")

                }
                if(data['material_type'] == 'webpage') {
                    var embed_code = qweb.render('MaterialDetails',
                    {
                        data: data['webpage_content']
                    });
                    $('.modal-title-lms').html(data['name'])
                    $('.modal-body').html(embed_code);
                    $('.embed-responsive').removeClass('embed-responsive');
                    $('#preview-modal').modal("show")
                }
            });
        }
    },
    _onClickEditButton: function(e){
        var material_id = $(e.currentTarget).data('material-id');
        var material_name = $(e.currentTarget).parent().parent();
        var port_number = window.location.host;
        var http = location.protocol;
        var slashes = http.concat("//");
        ajax.jsonRpc('/get/material', 'call',
        {
            'material_id': material_id,
        }).then(function(res){
            var name = res.name
            var temp = name.replaceAll(' ', '-');
            var url = slashes + port_number + '/material-edit/' + temp + '-'+material_id + '?fullscreen=0&enable_editor=1'
            window.location.href = url;
        })
    }

})

//websiteRootData.websiteRootRegistry.add(OpenModalWidget, '.card-body');
publicWidget.registry.OpenModalLms = OpenModalWidget;
return OpenModalWidget;

});

