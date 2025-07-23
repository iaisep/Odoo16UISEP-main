odoo.define('openeducat_parent_enterprise.my_child_tour', function (require) {
'use strict';

var tour = require("web_tour.tour");

tour.register('test_my_child', {
    test: true,
    url: '/my/child/',
},
    [
        {
            content: "select Sumita S Dani",
            extra_trigger: "#child_name",
            trigger: "h4:contains(Sumita S Dani)",
        },

    ]
);

});
