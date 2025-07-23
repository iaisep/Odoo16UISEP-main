odoo.define('openeducat_quiz.exam_tour', function (require) {
'use strict';

var tour = require("web_tour.tour");

tour.register('online_exam', {
    test: true,
    url: '/online-exams/1',
},
        [
            {
                content: "go to get_exam_details",
                trigger: "a[href*='/online-exams']"
            },
        ]
);

});
