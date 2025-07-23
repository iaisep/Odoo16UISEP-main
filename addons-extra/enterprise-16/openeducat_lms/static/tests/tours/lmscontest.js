odoo.define('openeducat_lms.lms_tour', function (require) {
'use strict';

var tour = require("web_tour.tour");

tour.register('lms_test', {
    test: true,
    url: '/courses',
},
        [
            {
                content: "select Introduction To Python Programming",
                extra_trigger: '#cat',
                trigger: 'span:contains(Programming)',
            },
        ]
);

});
