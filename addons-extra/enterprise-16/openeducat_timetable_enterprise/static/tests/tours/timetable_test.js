odoo.define('openeducat_timetable_enterprise.student_timetable', function (require) {
'use strict';

var tour = require("web_tour.tour");

tour.register('test_timetable', {
    test: true,
    url: '/student/timetable/1',
},
    [
        {
        content: "select Advanced Taxation",
        extra_trigger: "#subject_name",
        trigger: "span:contains(Advanced Taxation)",
        },
    ]
);

});
