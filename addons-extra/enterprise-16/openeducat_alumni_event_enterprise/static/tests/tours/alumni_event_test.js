odoo.define('openeducat_alumni_event_enterprise.alumni_event', function (require) {
'use strict';

var tour = require("web_tour.tour");

tour.register('alumni_event', {
    test: true,
    url: '/alumni/detail/1',
},
    [
        {
            content: "select Sports Event",
            extra_trigger: '#event',
            trigger: 'span:contains(Sports)',
        },
    ]
);

});
