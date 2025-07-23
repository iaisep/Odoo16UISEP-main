odoo.define('openeducat_attendance_enterprise.attendance_tour', function (require) {
'use strict';

var tour = require("web_tour.tour");

tour.register('test_attendance', {
    test: true,
    url: '/student/attendance/1',
},
    [
        {
        content: "select BOA-Sem-1",
        extra_trigger: '#test',
        trigger: 'span:contains(BOA-Sem-1)',
        },
    ]
);

});
