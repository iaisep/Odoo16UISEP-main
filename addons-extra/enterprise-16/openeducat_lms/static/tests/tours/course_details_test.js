odoo.define('openeducat_lms.lms_course_tour', function (require) {
'use strict';

var tour = require("web_tour.tour");

tour.register('course_details_test', {
    test: true,
    url: '/course-detail/1',
},
    [
        {
            content: "select Sumita S Dani",
            extra_trigger: "#course_name",
            trigger: "span:contains(Sumita S Dani)"
        }
    ]
);

});
