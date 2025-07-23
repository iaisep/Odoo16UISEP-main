odoo.define('openeducat_alumni_enterprise.alumni_details', function (require) {
'use strict';

var tour = require("web_tour.tour");

tour.register('alumni_detail', {
    test: true,
    url: '/alumni/detail/1',
},
    [
        {
            content: "go to alumni_group",
            trigger: 'a[href*="/alumni"]',
        },
//        {
//            content: "select AD-2017",
//            extra_trigger: "#alumni_name",
//            trigger: "span:contains(AD-2017)",
//        },
    ]
);

});
