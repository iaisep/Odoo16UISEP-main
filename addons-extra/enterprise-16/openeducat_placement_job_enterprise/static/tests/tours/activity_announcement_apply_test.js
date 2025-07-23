odoo.define('openeducat_placement_job_enterprise.activity_announcement_apply_tour', function (require) {
'use strict';

var tour = require("web_tour.tour");

tour.register('test_activity_announcement_apply', {
    test: true,
    url: '/activity/announcement/apply/1',
},
    [
        {
            content: " go to Activity_detail",
            trigger: "a[href*='/activity/announcement/detail/']"
        }
    ]
);

});
