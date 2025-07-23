odoo.define('openeducat_student_progression_enterprise.student_progression', function (require) {
'use strict';

var tour = require("web_tour.tour");

tour.register('test_student_progression', {
    test: true,
    url: '/student/progression/1',
},
    [
        {
            content: "select Mitchell Admin",
            extra_trigger: "#progression_created_by",
            trigger: "span:contains(Mitchell Admin)",
        }
    ]
);

});
