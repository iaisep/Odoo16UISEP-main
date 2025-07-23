odoo.define('openeducat_job_enterprise.campus_job_tour', function (require) {
'use strict';

var tour = require("web_tour.tour");

tour.register('test_campus_job', {
    test: true,
    url: '/campus/jobs',
},
    [
        {
            content: "select 602 Suyojan Complex",
            extra_trigger: '#street',
            trigger: 'span:contains(Suyojan)',
        },
    ]
);

});
