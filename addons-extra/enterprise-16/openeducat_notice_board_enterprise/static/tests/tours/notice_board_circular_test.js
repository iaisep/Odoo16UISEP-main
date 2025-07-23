odoo.define('openeducat_notice_board_enterprise.circular_tour', function (require) {
'use strict';

var tour = require("web_tour.tour");

tour.register('student_circular_list_view', {
    test: true,
    url: '/my/notice_board/circular/',
},
        [
            {
                content: "select Inter Batch Quiz Competition",
                extra_trigger: '#circular_name',
                trigger: "span:contains(Inter Batch Quiz Competition)",
            },
        ]
);

tour.register('parent_circular_list_view', {
    test: true,
    url: '/my/notice_board/circular/1',
},
        [
            {
                content: "select Inter Batch Quiz Competition",
                extra_trigger: '#circular_name',
                trigger: "span:contains(Inter Batch Quiz Competition)",
            },
        ]
);

});
