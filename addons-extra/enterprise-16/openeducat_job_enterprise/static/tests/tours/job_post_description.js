odoo.define('openeducat_job_enterprise.job_description_tour', function (require) {
'use strict';

var tour = require("web_tour.tour");

tour.register('test_job_description', {
    test: true,
    url: '/job_post/detail/post/1',
},
    [
        {
            content: "select Engineer",
            extra_trigger: '#job_post',
            trigger: 'p:contains(Engineer)',
        },
    ]
);

});
