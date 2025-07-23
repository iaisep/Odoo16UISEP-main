/* js for ipad view */

$(document).ready(function () {

    var url = window.location.href;
    var check_url = url.split("/")[3];
    if($('#wrapwrap').find('.quiz_completed_no_back').length == 1){
        if (history.pushState != undefined) {
            history.pushState(null, null, window.location.href);
        }
        history.back();
        history.forward();
        window.onpopstate = function () {
            history.go(1);
        };
    }

    if(check_url !==''){

        var pieces = url.split("/");

        var result = url.split("/");
        if(typeof pieces[5]!=='undefined'){
            pieces = pieces[5].split("/");
            result=result[4].split("/")
        }
        if(pieces == 'record'){
            window.localStorage.removeItem("end1");
        }
        else if(result == "score"){
            window.localStorage.removeItem("end1");
        }
        else{
            if($('#divCounter')){

                var hoursleft = parseInt($('#time_spent_hr').val());
                var minutesleft = parseInt($('#time_spent_minute').val());
                var secondsleft = parseInt($('#time_spent_second').val());
                var finishedtext = "Countdown finished!";
                var end1;
                if(localStorage.getItem("end1")) {
                    end1 = new Date(localStorage.getItem("end1"));
                } else {
                    end1 = new Date();
                    end1.setHours(end1.getHours()+hoursleft);
                    end1.setMinutes(end1.getMinutes()+minutesleft);
                    end1.setSeconds(end1.getSeconds()+secondsleft);
                }
                var counter = function () {
                        var now = new Date();
                        var diff = end1 - now;
                        diff = new Date(diff);

                        var milliseconds = parseInt((diff%1000)/100)
                        var sec = parseInt((diff/1000)%60)
                        var mins = parseInt((diff/(1000*60))%60)
                        var hours = parseInt((diff/(1000*60*60))%24);

                        if (hours < 10) {
                            hours = "0" + hours;
                        }
                        if (mins < 10) {
                            mins = "0" + mins;
                        }

                        if (sec < 10) {
                            sec = "0" + sec;
                        }
                        if(now >= end1) {
                            clearTimeout(interval);
                             localStorage.removeItem("end1");
                             localStorage.clear();
                            document.getElementById('divCounter').innerHTML = finishedtext;
                            window.location.href = $('#submit_exam').attr('href');
                        } else {
                            var value = hours + ":" + mins + ":" + sec;
                            localStorage.setItem("end1", end1);
                            if (document.getElementById('all_time')){
                            document.getElementById('all_time').innerHTML = value;}
                            if (document.getElementById('spanHrone')){
                            document.getElementById('spanHrone').innerHTML = hours;}
                            if (document.getElementById('spanMtone')){
                            document.getElementById('spanMtone').innerHTML = mins;}
                            if (document.getElementById('spanSnone')){
                            document.getElementById('spanSnone').innerHTML = sec;}
                        }
                    }
                var url = window.location.href;
                var pieces = url.split("/");
                if(typeof pieces[5]!=='undefined'){
                    pieces = pieces[4].split("/");
                }
                if(pieces == 'attempt'){
                     var interval = setInterval(counter, 1000);
                }
                $('.quiz_finish').on('click',function(e){
                    e.preventDefault();
                    var spent_time = $('#all_time').html();
                    $('#from_quiz_dynamic').append('<input type="hidden" name="t_spent_time" value="'+spent_time+'" />');
                });

                    $('#prev_timer').on('click',function(e){
                        var spent_time = $('#all_time').html();
                        var new_href = $(this).attr('href')+spent_time;
                        window.location.href = new_href;
                    });
            }
        }
    }
});

/* js for desktop & phone view */

$(document).ready(function () {

    var url = window.location.href;
    var check_url = url.split("/")[3];


    if(check_url !==''){

        var pieces = url.split("/");

        var result = url.split("/");
        if(typeof pieces[5]!=='undefined'){
            pieces = pieces[5].split("/");
            result=result[4].split("/")
        }
        if(pieces == 'record'){
            window.localStorage.removeItem("end1");
        }
        else if(result == "score"){
            window.localStorage.removeItem("end1");
        }
        else{
            if($('#divCounterone')){

                var hoursleft = parseInt($('#time_spent_hr').val());
                var minutesleft = parseInt($('#time_spent_minute').val());
                var secondsleft = parseInt($('#time_spent_second').val());
                var finishedtext = "Countdown finished!";
                var end1;
                if(localStorage.getItem("end1")) {
                    end1 = new Date(localStorage.getItem("end1"));
                } else {
                    end1 = new Date();
                    end1.setHours(end1.getHours()+hoursleft);
                    end1.setMinutes(end1.getMinutes()+minutesleft);
                    end1.setSeconds(end1.getSeconds()+secondsleft);
                }
                var counter = function () {
                        var now = new Date();
                        var diff = end1 - now;
                        diff = new Date(diff);

                        var milliseconds = parseInt((diff%1000)/100)
                        var sec = parseInt((diff/1000)%60)
                        var mins = parseInt((diff/(1000*60))%60)
                        var hours = parseInt((diff/(1000*60*60))%24);

                        if (hours < 10) {
                            hours = "0" + hours;
                        }
                        if (mins < 10) {
                            mins = "0" + mins;
                        }

                        if (sec < 10) {
                            sec = "0" + sec;
                        }
                        if(now >= end1) {
                            clearTimeout(interval);
                             localStorage.removeItem("end1");
                             localStorage.clear();
                            document.getElementById('divCounter').innerHTML = finishedtext;
                            window.location.href = $('#submit_exam').attr('href');
                        } else {
                            var value = hours + ":" + mins + ":" + sec;
                            localStorage.setItem("end1", end1);
                            if (document.getElementById('all_time')){
                            document.getElementById('all_time').innerHTML = value;}
                            if (document.getElementById('spanHr')){
                            document.getElementById('spanHr').innerHTML = hours;}
                            if (document.getElementById('spanMt')){
                            document.getElementById('spanMt').innerHTML = mins;}
                            if (document.getElementById('spanSn')){
                            document.getElementById('spanSn').innerHTML = sec;}
                        }
                    }
                var url = window.location.href;
                var pieces = url.split("/");
                if(typeof pieces[5]!=='undefined'){
                    pieces = pieces[4].split("/");
                }
                if(pieces == 'attempt'){
                     var interval = setInterval(counter, 1000);
                }
                $('.quiz_finish').on('click',function(e){
                    var spent_time = $('#all_time').html();
                    $('#from_quiz_dynamic').append('<input type="hidden" name="t_spent_time" value="'+spent_time+'" />');
                });

                    $('#prev_timer').on('click',function(e){
                        e.preventDefault();
                        var spent_time = $('#all_time').html();
                        var new_href = $(this).attr('href')+spent_time;
                        window.location.href = new_href;
                    });
            }
        }
    }
});

/*
$(document).ready(function () {
    $("#from_quiz_dynamic").on("submit", function(e) {
        var postData = $(this).serializeArray();
        var formURL = $(this).attr("action");
        $.ajax({
            url: formURL,
            type: "POST",
            data: postData,
            success: function(data, textStatus, jqXHR) {
                console.info("Status",textStatus);
            },
            error: function(jqXHR, status, error) {
                console.log(status + ": " + error);
            }
        });
        e.preventDefault();
    });
});*/
