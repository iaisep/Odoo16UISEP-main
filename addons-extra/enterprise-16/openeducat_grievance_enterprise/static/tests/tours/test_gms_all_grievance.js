odoo.define('openeducat_grievance_enterprise.test_gms_all_grievance', function (require) {
'use strict';

var tour = require("web_tour.tour");

tour.register('test_gms_all_grievance', {
    test: true,
    url: '/my/grievances',
},
    [
        {
            content: "select Grievance About Grades",
            extra_trigger: '#gms_subject_list',
            trigger: "span:contains(Grievance About Grades)",
        },
    ]
);

tour.register('test_gms_faculty_all_grievance', {
    test: true,
    url: '/my/grievances',
},
    [
        {
            content: "select Grievance About parking",
            extra_trigger: '#gms_subject_list',
            trigger: "span:contains(Grievance About parking)",
        },
    ]
);
});
