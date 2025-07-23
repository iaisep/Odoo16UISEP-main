odoo.define('openeducat_grievance_enterprise.test_gms_grievance_edit', function (require) {
'use strict';

var tour = require("web_tour.tour");

tour.register('test_gms_grievance_edit', {
    test: true,
    url: '/my/grievance/grievance-edit/1',
},
    [
        {
            content: "select Gradessss",
            extra_trigger: '#edit_subject',
            trigger: 'form:has(input[name="subject"])',
        },
    ]
);

tour.register('test_gms_faculty_grievance_edit', {
    test: true,
    url: '/my/grievance/grievance-edit/2',
},
    [
        {
            content: "select parking",
            extra_trigger: '#edit_subject',
            trigger: 'form:has(input[name="subject"])',
        },
    ]
);
});
