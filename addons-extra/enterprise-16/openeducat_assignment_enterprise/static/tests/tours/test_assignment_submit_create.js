odoo.define('openeducat_assignment_enterprise.assignment_submitted_tour', function (require) {
'use strict';

var tour = require("web_tour.tour");

tour.register('test_assignment_submit_create', {
    test: true,
    url: '/assignment/submited/1',
},
    [
        {
            content: "select LRTP - 001 - Asg - 009",
            extra_trigger: '#name',
            trigger: 'span:contains(LRTP-001-Asg-001)',
        },
    ]
);

});
