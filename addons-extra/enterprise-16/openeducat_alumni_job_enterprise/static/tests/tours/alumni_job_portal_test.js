odoo.define('openeducat_alumni_job_enterprise.alumni_portal_tour', function (require) {
'use strict';

var tour = require("web_tour.tour");

tour.register('test_alumni_portal', {
    test: true,
    url: '/alumni/job/list/1',
},
    [
        {
            content: "select Full Time",
            trigger: 'a[href*="/alumni/job"]',
        },
    ]
);

});
