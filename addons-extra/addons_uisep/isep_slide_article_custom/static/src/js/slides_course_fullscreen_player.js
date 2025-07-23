odoo.define('isep_slide_article_custom.fullscreen', function (require) {
    "use strict";

    var core = require('web.core');
    var QWeb = core.qweb;
    var Fullscreen = require('@website_slides/js/slides_course_fullscreen_player')[Symbol.for("default")];

    Fullscreen.include({
        /**
         * Extiende el método _renderSlide para personalizar el contenido
         *
         * @private
         * @override
         */
        _renderSlide: async function () {
            var def = this._super.apply(this, arguments);
            var $content = this.$('.o_wslides_fs_content');
            var slide = this.get('slide');

            if (this.get('slide').category === "article") {
                console.log("Adding custom div to article slide.");
                try {
                    const slideData = await this._rpc({
                        route: '/slides/slide/get_slide_data_custom',
                        params: { slide_id: slide.id },
                    });

                    slide.msn_custom = slideData.msn_custom || false;
                } catch (error) {
                    console.error("Error fetching slide data:", error);
                    slide.msn_custom = false; // En caso de error, asumimos que msn_custom es falso
                }

                if (slide.msn_custom) {
                    console.log("msn_custom is true, rendering combined content.");

                    var customTemplateHtml = QWeb.render('custom_html_template', { slide: slide });

                    var combinedContent = `
                        <div class="o_wslide_fs_article_content bg-white block w-100 overflow-auto p-3">
                            ${customTemplateHtml}
                            ${slide.htmlContent}
                        </div>
                    `;

                    $content.empty().append(combinedContent);
                } else {
                    console.log("msn_custom is false, rendering normal content.");

                    var $wpContainer = $('<div>')
                        .addClass('o_wslide_fs_article_content bg-white block w-100 overflow-auto p-3');

                    $wpContainer.html(slide.htmlContent);

                    $content.empty().append($wpContainer);
                }
            }

            return Promise.all([def]);
        },
    });
});
