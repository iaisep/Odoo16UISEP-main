odoo.define('openeducat_assignment_enterprise.assignment_data_tour', function (require) {
'use strict';

var tour = require("web_tour.tour");

tour.register('test_assignment', {
    test: true,
    url: '/assignment/data/1',
},
    [
        {
            content: "select BOA Sem-1-Asg-001",
            extra_trigger: '#name',
            trigger: "span:contains(BOA Sem-1-Asg-001)",
        },
    ]
);

});
