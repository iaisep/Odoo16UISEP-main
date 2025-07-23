odoo.define('openeducat_digital_library.library_material', function (require) {
'use strict';

var tour = require("web_tour.tour");

tour.register('category_detail', {
    test: true,
    url: '/digital-library/material/1',
},
    [
        {
            content: "go to digital_library",
            trigger: "form[action^='/digital-library'] .btn"
        },
    ]
);

});
