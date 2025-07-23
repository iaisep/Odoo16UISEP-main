-- disable flywire payment provider
UPDATE payment_provider
   SET flywire_shared_key = NULL,
       flywire_api_key = NULL,
       flywire_frontend_api_key = NULL,
       flywire_recipient_priority = NULL,
       flywire_default_recipient_id = NULL;
