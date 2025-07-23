odoo.define('openeducat_exam_enterprise.exam_tour', function (require) {
'use strict';

var tour = require("web_tour.tour");

tour.register("student_exam" ,{
    test: true,
    url: "/student/exam/1"
},
    [
        {
            content: "go to portal_student_exam_form",
            trigger: "a[href^='/student/exam/data/1']"
        },
    ]
);

});
