odoo.define('openeducat_assignment_enterprise.assignment_list_tour', function (require) {
'use strict';

var tour = require("web_tour.tour");

tour.register('test_assignment_submit', {
    test: true,
    url: '/submited/assignment/list/1',
},
    [
        {
            content: "select BOA Sem-1-Asg-001",
            extra_trigger: '#assignment_name',
            trigger: 'span:contains(BOA Sem-1-Asg-001)'
        },
    ]
);

});
