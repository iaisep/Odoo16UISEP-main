odoo.define('openeducat_grievance_enterprise.test_gms_grievance_submit', function (require) {
'use strict';

var tour = require("web_tour.tour");

tour.register('test_gms_grievance_submit', {
    test: true,
    url: '/my/grievance/grievance-form',
},
    [
        {
            content: "select Grievance About Grades",
            extra_trigger: '#subject_input',
            trigger: 'form:has(input[name="subject"])',
        },
    ]
);

tour.register('test_gms_grievance_submit_state', {
    test: true,
    url: '/my/grievances',
},
    [
        {
            content: "select Grievance About Grades",
            trigger: 'a[href*="/my/grievance/submit/gri0001-1"]',
        },
    ]
);


tour.register('test_gms_faculty_grievance_submit', {
    test: true,
    url: '/my/grievance/grievance-form',
},
    [
        {
            content: "select Grievance About parking",
            extra_trigger: '#subject_input',
            trigger: 'form:has(input[name="subject"])',
        },
    ]
);

tour.register('test_gms_faculty_grievance_submit_state', {
    test: true,
    url: '/my/grievances',
},
    [
        {
            content: "select Grievance About parking",
            trigger: 'a[href*="/my/grievance/submit/gri0002-2"]',
        },
    ]
);
});
