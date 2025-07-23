odoo.define('openeducat_grievance_enterprise.test_gms_parent_grievance_detail', function (require) {
'use strict';

var tour = require("web_tour.tour");

tour.register('test_gms_parent_grievance_detail', {
    test: true,
    url: '/my/grievance/detail/1/3',
},
    [
        {
            content: "select Hostel Service irregular",
            extra_trigger: '#gms_subject',
            trigger: "span:contains(Hostel Service irregular)",
        },
    ]
);

tour.register('test_gms_parent_grievance_satisfied', {
    test: true,
    url: '/my/grievance/detail/1/3',
},
    [
        {
            content: "select Hostel Service irregular",
            trigger: 'a[href*="/my/grievance/satisfied/1/3"]',
        },
    ]
);

tour.register('test_gms_parent_grievance_not_satisfied', {
    test: true,
    url: '/my/grievance/detail/1/3',
},
    [
        {
            content: "select Hostel Service irregular",
            trigger: 'a[href*="/my/grievance/not-satisfied/1/3"]',
        },
    ]
);

});
