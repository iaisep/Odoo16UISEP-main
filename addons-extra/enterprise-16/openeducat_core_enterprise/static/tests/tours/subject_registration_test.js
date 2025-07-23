odoo.define('openeducat_core_enterprise.subject_registration_tour', function (require) {
'use strict';

var tour = require("web_tour.tour");

tour.register('test_subject_registration', {
    test: true,
    url: '/subject/registration/1',
},
    [
        {
            content: "go to portal_craete_subject_registration",
            trigger: "a[href*='/subject/registration/create/']"
        },
    ]
);

});
