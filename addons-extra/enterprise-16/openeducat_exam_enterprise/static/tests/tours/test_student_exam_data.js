odoo.define('openeducat_exam_enterprise.exam_data_tour', function (require) {
'use strict';

var tour = require("web_tour.tour");

tour.register("student_exam_data" ,{
    test: true,
    url: "/student/exam/data/1"
},
    [
        {
            content: "select BOA-Exam-001",
            extra_trigger: "#exam_name",
            trigger: "span:contains(BOA-Exam-001)"
        },
    ]
);

});
