odoo.define('openeducat_job_enterprise.job_post_tour', function (require) {
'use strict';

var tour = require("web_tour.tour");

tour.register('test_job', {
    test: true,
    url: '/job_post/detail/1',
},
    [
        {
            content: "select Application Engineer",
            extra_trigger: '#job_post_field',
            trigger: 'h3:contains(Application Engineer)',
        },
    ]
);

});
