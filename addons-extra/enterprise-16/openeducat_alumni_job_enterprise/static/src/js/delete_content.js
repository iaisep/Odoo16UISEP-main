odoo.define('openeducat_alumni_job_enterprise.delete_content', function (require) {
    'use strict';

    $(document).ready(function(){

        $('.delete_content').on('click', function(e){
            var a = $(this).data('job_id');
            $('.ok_button').attr('href','/alumni/job/delete/' + a)
            $('#open_modal').modal('show');

        });
    });
});
