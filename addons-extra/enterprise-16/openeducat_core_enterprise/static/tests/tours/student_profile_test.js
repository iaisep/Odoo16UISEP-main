odoo.define('openeducat_core_enterprise.student_tour', function (require) {
'use strict';

var tour = require("web_tour.tour");

tour.register('test_student_profile', {
    test: true,
    url: '/student/profile/1',
},
    [
        {
            content: "select Sumita S Dani",
            extra_trigger: '#student_name',
            trigger: "h3:contains(Sumita S Dani)",
        },
    ]
);

});
