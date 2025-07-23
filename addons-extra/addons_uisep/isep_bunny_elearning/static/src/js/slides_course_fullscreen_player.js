odoo.define('isep_bunny_elearning.fullscreen_bunny', function (require) {
    'use strict';
    var core = require('web.core');
    var QWeb = core.qweb;
    var rpc = require('web.rpc');
    var Fullscreen = require('@website_slides/js/slides_course_fullscreen_player')[Symbol.for("default")];

    var findSlide = function (slideList, matcher) {
        var slideMatch = _.matcher(matcher);
        return _.find(slideList, slideMatch);
    };

    Fullscreen.include({
        xmlDependencies: (Fullscreen.prototype.xmlDependencies || []).concat(
            ["/isep_bunny_elearning/static/src/xml/website_slides_fullscreen.xml"]
        ),
        _preprocessSlideData: function (slidesDataList) {
            var res = this._super.apply(this, arguments);

            slidesDataList.forEach(function (slideData, index) {
                if (slideData.category === 'bunny') {
                    slideData.embedUrl = $(slideData.embedCode).attr('src');
                    slideData.hasQuestion = !!slideData.hasQuestion;
                    try {
                        if (!(slideData.isTimer) && !(slideData.hasQuestion) && !(slideData.is_tincan)) {
                            slideData._autoSetDone = true;
                        }
                    }
                    catch {
                        if (!(slideData.hasQuestion)) {
                            slideData._autoSetDone = true;
                        }
                    }
                }
            });
            return res;
        },

        /**
         * Extend the _renderSlide method so that slides of type "bunny"
         * are also taken into account and rendered correctly
         *
         * @private
         * @override
         */

        _renderSlide: function (){
            var def = this._super.apply(this, arguments);
            var $content = this.$('.o_wslides_fs_content');
            var slideId = this.get('slide');
            if (slideId.category === "bunny"){
                $content.html(QWeb.render('website.slides.fullscreen.content',{widget: this}));
            }
            return Promise.all([def]);
        },

    });


    

    
    
});