odoo.define('openeducat_notice_board_enterprise.notice_tour', function (require) {
'use strict';

var tour = require("web_tour.tour");

tour.register('student_notice_list_view', {
    test: true,
    url: '/my/notice_board/notice/',
},
        [
            {
                content: "select BOA Student's Misbehaviour in Class",
                extra_trigger: '#notice_name',
                trigger: "span:contains(BOA Student's Misbehaviour in Class)",
            },
        ]
);

tour.register('student_notice_view', {
    test: true,
    url: '/notice_board/notice/1/1',
},
        [
            {
                content: "select Misbehaviour Fine",
                extra_trigger: '#notice_subject',
                trigger: "span:contains(Misbehaviour Fine)",
            },
        ]
);

tour.register('parent_notice_list_view', {
    test: true,
    url: '/my/notice_board/notice/1',
},
        [
            {
                content: "select BOA Student's Misbehaviour in Class",
                extra_trigger: '#notice_name',
                trigger: "span:contains(BOA Student's Misbehaviour in Class)",
            },
        ]
);

tour.register('parent_notice_view', {
    test: true,
    url: '/notice_board/notice/1/1',
},
        [
            {
                content: "select Misbehaviour Fine",
                extra_trigger: '#notice_subject',
                trigger: "span:contains(Misbehaviour Fine)",
            },
        ]
);

});
