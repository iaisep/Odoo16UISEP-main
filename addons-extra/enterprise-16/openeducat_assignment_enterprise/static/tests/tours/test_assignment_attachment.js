odoo.define('openeducat_assignment_enterprise.assignment_download_tour', function (require) {
'use strict';

var tour = require("web_tour.tour");

tour.register('test_assignment_attachment', {
    test: true,
    url: '/assignment/download/',
},
    [
        {
            content: "an attachment",
            extra_trigger: '#name',
            trigger: 'a:contains(an)',
        },
    ]
);

});
