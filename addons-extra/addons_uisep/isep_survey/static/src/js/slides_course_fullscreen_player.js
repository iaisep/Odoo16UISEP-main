odoo.define('isep_survey.fullscreen', function (require) {
    "use strict";
    
    var core = require('web.core');
    var QWeb = core.qweb;
    var Fullscreen = require('@website_slides/js/slides_course_fullscreen_player')[Symbol.for("default")];
    
    Fullscreen.include({
        /**
         * Extend the _renderSlide method so that slides of category "certification"
         * are also taken into account and rendered correctly
         *
         * @private
         * @override
         */
        _renderSlide: async function () {
            var def = this._super.apply(this, arguments);
            var $content = this.$('.o_wslides_fs_content');
        
            // Check if the slide belongs to the "certification" category
            if (this.get('slide').category === "certification") {
                var slide = this.get('slide');
                console.log("Initial Slide Data:", slide);

                try {
                    const slideData = await this._rpc({
                        route: '/slides/slide/get_slide_data_description',
                        params: { slide_id: slide.id },
                    });
                    
                    slide.slide_description = slideData.slide_description || " ";
                    slide.survey_description = slideData.survey_description || " ";
                } catch (error) {
                    console.error("Error fetching slide data:", error);
                    slide.slide_description = "slide_description no disponible";
                    slide.survey_description = "survey_description no disponible";
                }

                $content.html(QWeb.render('website.slides.fullscreen.certification', {
                    widget: this,
                    slide: slide,
                    slide_description: slide.slide_description,
                    survey_description: slide.survey_description,
                }));
            }

            return Promise.all([def]);
        },
    });
});