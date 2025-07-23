odoo.define('openeducat_alumni_enterprise.alumni_page_tour', function (require) {
'use strict';

var tour = require("web_tour.tour");

tour.register('alumni_page', {
    test: true,
    url: '/alumni',
},
    [
        {
            content: "go to alumni_detail",
            trigger: 'a[href*="/alumni/detail"]',
        },
    ]
);

});
