odoo.define('openeducat_alumni_job_enterprise.alumni_job_tour', function (require) {
'use strict';

var tour = require("web_tour.tour");

tour.register('test_alumni_job', {
    test: true,
    url: '/alumni/job',
},
    [
        {
            content: "Add new Job Post",
            trigger: ".mt32 form[action^='/alumni/job/submit'] .btn",
        }
    ]
);

});
