/* global Stripe */
odoo.define('payment_flywire.payment_form', require => {
    'use strict';

    var ajax = require('web.ajax');

    const checkoutForm = require('payment.checkout_form');
    const manageForm = require('payment.manage_form');

    const flywireMixin = {

        /**
         * Redirect the customer to flywire hosted payment page.
         *
         * @override method from payment.payment_form_mixin
         * @private
         * @param {string} provider - The provider of the payment option's acquirer
         * @param {number} paymentOptionId - The id of the payment option handling the transaction
         * @param {object} processingValues - The processing values of the transaction
         * @return {undefined}
         */
        _processRedirectPayment: function (provider, paymentOptionId, processingValues) {
            if (provider !== 'flywire') {
                return this._super(...arguments);
            }
            
            
        },

        /**
         * Prepare the options to init the flywire object
         *
         * Function overriden in internal module
         *
         * @param {object} processingValues
         * @return {object}
        */
        _prepareflywireOptions: function () {
            return {};
        },
    };

    checkoutForm.include(flywireMixin);
    manageForm.include(flywireMixin);

});