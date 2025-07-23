odoo.define('isep_practices', function (require) {

    "use strict";
    /*var Model = require('res.partner');*/


    $(function() {
        let date_start = '';
        let date_final = '';

        if (date_final=='' || date_start==''){
            $('#submit').attr("disabled", true);
            $('#submit').mouseover(function(){
                if ($("#submit").prop("disabled")) {
                    alert("Verifique que la fecha de inicio no sea menor a la fecha inicial");
                }
            });
        }

        $('body').on('change', '#start_date, #final_date', function(e) {
                date_final = $("#final_date").val()
                date_start = $("#start_date").val()
                if ((date_final=='' || date_start=='')){

                        $('#submit').attr("disabled", true);

                }else if (date_start>=date_final){
                        $('#submit').attr("disabled", true);
                }
                else{
                        $('#submit').attr("disabled", false);
                }
        });

        $('#submit').mouseover(function(){
            if ($("#submit").prop("disabled")) {
                alert("Verifique que la fecha de inicio no sea menor a la fecha inicial");
            }
        });

        $('#code_zip').select2();

        $(document).ready(function(){
            $("#code_zip").change(function (){
                var ini = $('select[name=res_better_zip]').val();
                //alert( $('select[name=res_better_zip]').val());
                //$("#code_zip").val($('select[name=res_better_zip]').val());
                //$("#code_zip").selectmenu('refresh', true);
               // $('select[name=res_better_zip]').attr('selected', 'selected');
                $("#code_zip").attr("selected",true);
                //alert($('#code_zip').val());
            });

        });
        /*
        $(document).ready(function (){
            $("select[name=res_better_zip]").change(function(){
                //alert($('select[name=res_better_zip]').val());
                //$('input[name=valor1]').val($(this).val());
                $('select[name=res_better_zip]').val();
                $('#valor3').val($(this).val());
             });

        });
        */

        //console.log(models)
    });
});









