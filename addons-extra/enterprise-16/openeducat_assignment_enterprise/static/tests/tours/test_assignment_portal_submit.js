odoo.define('openeducat_assignment_enterprise.assignment_submit_tour', function (require) {
'use strict';

var tour = require("web_tour.tour");

tour.register('test_assignment_portal_submit', {
    test: true,
    url: '/assignment/submit/1',
},
    [
        {
            content: "search LRTP - 001 - Asg - 009",
            extra_trigger: '#name',
            trigger: 'form:has(input[name="search"])',
        },
    ]
);

});
