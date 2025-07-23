odoo.define('openeducat_grievance_enterprise.test_gms_parent_grievance_submit', function (require) {
'use strict';

var tour = require("web_tour.tour");

tour.register('test_gms_parent_grievance_submit', {
    test: true,
    url: '/my/grievance/grievance-form/1',
},
    [
        {
            content: "select Hostel Service irregular",
            extra_trigger: '#subject_input',
            trigger: 'form:has(input[name="subject"])',
        },
    ]
);

tour.register('test_gms_parent_grievance_submit_state', {
    test: true,
    url: '/my/grievances/1',
},
    [
        {
            content: "select Hostel Service irregular",
            trigger: 'a[href*="/my/grievance/submit/1/gri0003-3"]',
        },
    ]
);

});
