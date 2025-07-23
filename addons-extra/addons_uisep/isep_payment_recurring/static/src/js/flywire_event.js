odoo.define('isep_payment_recurring.flywire_event', function (require) {
    'use strict';

    var ajax = require('web.ajax');

    $(document).ready(function () {
        var invoice_id = window.invoice_id;
        // console.log("Invoice ID:", invoice_id);
        // Confirmar sesión de pago
        window.addEventListener("message", (event) => {
            // IMPORTANT: check the origin of the data
            if (event.origin.indexOf(".flywire.com") > 0) {
                // The data was sent from Flywire, we can check now if tokenization was successful
                const result = event.data;
                console.log("result", result);
                console.log("Invoice ID:", invoice_id);
                if (result.success) {
                    // The tokenization was successful and the confirm url has been returned
                    const confirm_url = event.data.confirm_url.url;
                    // const confirmUrl = event.data.confirmUrl;
                    console.log("confirUrl", confirm_url); 
                    // use confirmUrl as required
                    ajax.jsonRpc('/flywire/confirm_checkout_session', 'call', {
                        confirm_url: confirm_url,
                        invoice_id: invoice_id,
                    }).then(function (data) {
                        if (data.status === 'success') {
                            var payment_method = data.payment_method;
                            var mandate = data.mandate;
                            console.log("data", payment_method,mandate);

                            // Crear pago
                            ajax.jsonRpc('/flywire/create_payment', 'call', {
                                payment_method: payment_method,
                                mandate: mandate,
                                invoice_id: invoice_id
                            }).then(function (data) {
                                if (data.status === 'success') {
                                    console.log('Pago creado:', data);
                                } else {
                                    console.error('Error creando el pago:', data.message, payment_method, mandate, invoice_id);
                                }
                            });
                        } else {
                            console.error('Error confirmando la sesión:', data.message);
                        }
                    });
                } else {
                    // handle tokenization failure accordingly
                    console.error('Error en la tokenización:', result.message);
                }
            } else {
                // The data was NOT sent from from Flywire
                // Do not use it. This else branch is
                // here just for clarity, you usually shouldn't need it.
                return;
            }
        });
    });
});