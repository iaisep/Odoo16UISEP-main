odoo.define('openeducat_meeting_enterprise.meeting_data_tour', function (require) {
'use strict';

var tour = require("web_tour.tour");

tour.register("test_meeting_information_data" ,{
    test: true,
    url: "/meeting/information/data/1/1"
},
    [
        {
            content: "select Parent Teacher Meeting",
            extra_trigger: "#meeting_name",
            trigger: "span:contains(Parent Teacher Meeting)"
        },
    ]
);

});
