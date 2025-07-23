odoo.define('openeducat_grievance_enterprise.test_gms_grievance_delete', function (require) {
'use strict';

var tour = require("web_tour.tour");

tour.register('test_gms_grievance_delete', {
    test: true,
    url: '/my/grievance/detail/1',
},
    [
        {
            content: "select Grievance About Grades",
            trigger: 'a[href*="/my/grievance/cancel/gri0001-1"]',
        },
    ]
);

});
