odoo.define('openeducat_quiz.quiz_rule_tour', function (require) {
'use strict';

var tour = require("web_tour.tour");

tour.register('quiz_rules', {
    test: true,
    url: '/quiz/rules/1',
},
        [
            {
                content: "go to get_exam_details",
                trigger: "a[href*='/online-exams']"
            },
        ]
);

});
