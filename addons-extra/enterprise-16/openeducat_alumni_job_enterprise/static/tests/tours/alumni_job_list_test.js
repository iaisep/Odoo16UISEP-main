odoo.define('openeducat_alumni_job_enterprise.alumni_job_list_tour', function (require) {
'use strict';

var tour = require("web_tour.tour");

tour.register('test_alumni_job_list', {
    test: true,
    url: '/alumni/job/list/1',
},
    [
        {
            content: "click on 'Alumni Job Post' button",
            trigger: "a[href*='/alumni/job']"
        },
        {
            content: "go to portal_alumni_job_post_list_details",
            trigger: "a[href*='alumni/job/details/']",
        },
    ]
);

});
