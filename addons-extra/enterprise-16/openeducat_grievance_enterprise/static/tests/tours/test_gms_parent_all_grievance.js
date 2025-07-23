odoo.define('openeducat_grievance_enterprise.test_gms_parent_all_grievance', function (require) {
'use strict';

var tour = require("web_tour.tour");

tour.register('test_gms_parent_all_grievance', {
    test: true,
    url: '/my/grievances/1',
},
    [
        {
            content: "select Grievance About Grades",
            extra_trigger: '#gms_subject_list',
            trigger: "span:contains(Grievance About Grades)",
        },
    ]
);
});
