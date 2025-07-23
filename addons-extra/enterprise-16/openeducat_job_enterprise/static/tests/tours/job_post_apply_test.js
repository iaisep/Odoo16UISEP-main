odoo.define('openeducat_job_enterprise.job_position_tour', function (require) {
'use strict';

var tour = require("web_tour.tour");

tour.register('test_job_apply', {
    test: true,
    url: '/job/post/apply/1',
},
    [
        {
            content: "add new Job Position",
            trigger: 'form[action^="/form/submit"] .btn-primary',
        },
    ]
);

});
