odoo.define('openeducat_digital_library.library_page', function (require) {
'use strict';

var tour = require("web_tour.tour");

tour.register('digital_library', {
    test: true,
    url: '/digital-library/page/1',
},
    [
        {
            content: "go to digital_library",
            trigger: "a[href*='/digital-library']"
        }
    ]
);

});
