odoo.define('openeducat_grievance_enterprise.test_gms_parent_grievance_edit', function (require) {
'use strict';

var tour = require("web_tour.tour");

tour.register('test_gms_parent_grievance_edit', {
    test: true,
    url: '/my/grievance/grievance-edit/1/3',
},
    [
        {
            content: "select Hostel Servicesssss",
            extra_trigger: '#edit_subject',
            trigger: 'form:has(input[name="subject"])',
        },
    ]
);
});
