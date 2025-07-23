odoo.define('openeducat_alumni_job_enterprise.job_details_tour', function (require) {
'use strict';

var tour = require("web_tour.tour");

tour.register("test_alumni_job_details", {
    test: true,
    url: '/alumni/job/details/1',
},
    [
        {
            content: "select Ahmedabad",
            extra_trigger: "#alumni_city",
            trigger: "span:contains(Ahmedabad)"
        }
    ]
);

});
