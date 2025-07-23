odoo.define('openeducat_grievance_enterprise.test_gms_grievance_detail', function (require) {
'use strict';

var tour = require("web_tour.tour");

tour.register('test_gms_grievance_detail', {
    test: true,
    url: '/my/grievance/detail/1',
},
    [
        {
            content: "select Grievance About Grades",
            extra_trigger: '#gms_subject',
            trigger: "span:contains(Grievance About Grades)",
        },
    ]
);

tour.register('test_gms_grievance_satisfied', {
    test: true,
    url: '/my/grievance/detail/1',
},
    [
        {
            content: "select Grievance About Grades",
            trigger: 'a[href*="/my/grievance/satisfied/gri0001-1"]',
        },
    ]
);

tour.register('test_gms_grievance_not_satisfied', {
    test: true,
    url: '/my/grievance/detail/1',
},
    [
        {
            content: "select Grievance About Grades",
            trigger: 'a[href*="/my/grievance/not-satisfied/gri0001-1"]',
        },
    ]
);

tour.register('test_gms_grievance_appeal_submit', {
    test: true,
    url: '/my/grievance/appeal/1',
},
    [
        {
            content: "select Grievance About Grades",
            extra_trigger: '#subject_input',
            trigger: 'form:has(input[name="subject"])',
        },
    ]
);

tour.register('test_gms_grievance_appeal', {
    test: true,
    url: '/my/grievance/detail/1',
},
    [
        {
            content: "select Grievance About Grades",
            extra_trigger: '#gms_subject',
            trigger: 'a[href*="/my/grievance/appeal/gri0001-1"]',
        },
    ]
);

tour.register('test_gms_faculty_grievance_detail', {
    test: true,
    url: '/my/grievance/detail/2',
},
    [
        {
            content: "select Grievance About parking",
            extra_trigger: '#gms_subject',
            trigger: "span:contains(Grievance About parking)",
        },
    ]
);


});
